# 09｜Spring Web URL 解析常见错误

对于 HTTP 请求，首先要处理的就是 URL，所以今天我们就先来介绍下，在 URL 的处理上，Spring 都有哪些经典的案例。

**案例 1：当 @PathVariable 遇到 /**

```java
@RestController
@Slf4j
public class HelloWorldController {
    @RequestMapping(path = "/hi1/{name}", method = RequestMethod.GET)
    public String hello1(@PathVariable("name") String name) {
        return name;
    }
}
```

当我们使用 http://localhost:8080/hi1/xiaoming 访问这个服务时，会返回"xiaoming"，即 Spring 会把 name 设置为 URL 中对应的值。

但是假设这个 name 中含有特殊字符 / 时，例如 http://localhost:8080/hi1/xiao/ming，会如何？具体错误如下所示：

![image-20220801221940581](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202208012219747.png)

但是当 name 的字符串以 / 结尾时，/ 会被自动去掉。例如我们访问 http://localhost:8080/hi1/xiaoming/，Spring 并不会报错，而是返回 xiaoming。

针对这两种类型的错误，应该如何理解并修正呢？

- 案例解析

这两种错误都是 URL 匹配执行方法的相关问题，所以我们有必要先了解下 URL 匹配执行方法的大致过程。参考 `AbstractHandlerMethodMapping#lookupHandlerMethod`：

```java
@Nullable
protected HandlerMethod lookupHandlerMethod(
    String lookupPath, HttpServletRequest request) throws Exception {
    List<Match> matches = new ArrayList<>();
    //尝试按照 URL 进行精准匹配
    List<T> directPathMatches = this.mappingRegistry.getMappingsByUrl(lookupPath);
    if (directPathMatches != null) {
        //精确匹配上，存储匹配结果
        addMatchingMappings(directPathMatches, matches, request);
    }
    if (matches.isEmpty()) {
        //没有精确匹配上，尝试根据请求来匹配
        addMatchingMappings(this.mappingRegistry.getMappings().keySet(), matches, request);
    }

    if (!matches.isEmpty()) {
        Comparator<Match> comparator = new MatchComparator(getMappingComparator(request));
        matches.sort(comparator);
        Match bestMatch = matches.get(0);
        if (matches.size() > 1) {
            //处理多个匹配的情况
        }
        //省略其他非关键代码
        return bestMatch.handlerMethod;
    }
    else {
        //匹配不上，直接报错
        return handleNoMatch(this.mappingRegistry.getMappings().keySet(), lookupPath, request);
    }
}
```

大体分为这样几个基本步骤。

1. 根据 Path 进行精确匹配

这个步骤执行的代码语句是"this.mappingRegistry.getMappingsByUrl(lookupPath)"，实际上，它是查询 MappingRegistry#urlLookup，它的值可以用调试视图查看，如下图所示：

![image-20220801222343140](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202208012223197.png)

显然，http://localhost:8080/hi1/xiao/ming 的 lookupPath 是"/hi1/xiao/ming"，并不能得到任何精确匹配。这里需要补充的是，"/hi1/{name}"这种定义本身也没有出现在 urlLookup 中。

2. 假设 Path 没有精确匹配上，则执行模糊匹配

在步骤 1 匹配失败时，会根据请求来尝试模糊匹配，待匹配的匹配方法可参考下图：

![image-20220801222609581](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202208012226641.png)

显然，"/hi1/{name}"这个匹配方法已经出现在待匹配候选中了。具体匹配过程可以参考方法 RequestMappingInfo#getMatchingCondition：

当使用 http://localhost:8080/hi1/xiaoming 访问时，其中 patternsCondition 是可以匹配上的。实际的匹配方法执行是通过 AntPathMatcher#match 来执行。

但是当我们使用 http://localhost:8080/hi1/xiao/ming 来访问时，AntPathMatcher 执行的结果是"/hi1/xiao/ming"匹配不上"/hi1/{name}"。

3. 根据匹配情况返回结果

如果找到匹配的方法，则返回方法；如果没有，则返回 null。

http://localhost:8080/hi1/xiao/ming 因为找不到匹配方法最终报 404 错误。追根溯源就是 AntPathMatcher 匹配不了"/hi1/xiao/ming"和"/hi1/{name}"。

那 http://localhost:8080/hi1/xiaoming/ 为什么没有报错而是直接去掉了 /。（这里可以参考负责执行 AntPathMatcher 匹配的 PatternsRequestCondition#getMatchingPattern）在 useTrailingSlashMatch 这个参数启用时（默认启用），会把 Pattern 结尾加上 / 再尝试匹配一次。

- 问题修正

```java
private AntPathMatcher antPathMatcher = new AntPathMatcher();

@RequestMapping(path = "/hi1/**", method = RequestMethod.GET)
public String hi1(HttpServletRequest request) {
    String path = (String) request.getAttribute(
        HandlerMapping.PATH_WITHIN_HANDLER_MAPPING_ATTRIBUTE);
    //matchPattern 即为"/hi1/**"
    String matchPattern = (String) request.getAttribute(
        HandlerMapping.BEST_MATCHING_PATTERN_ATTRIBUTE);
    return antPathMatcher.extractPathWithinPattern(matchPattern, path);
}
```

当然也存在一些其他的方案，例如对传递的参数进行 URL 编码以避免出现 /。

**案例 2：错误使用 @RequestParam、@PathVarible 等注解**

我们去获取一个请求参数 name，我们会定义如下：

```java
@RequestParam("name") String name
```

我们会发现变量名称大概率会被定义成 RequestParam 值。所以我们是不是可以用下面这种方式来定义：

```java
@RequestParam String name
```

这种方式确实是可以的，本地测试也能通过。

但当我们的项目 pom.xml 配置如下时：

```xml
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-compiler-plugin</artifactId>
  <configuration>
    <debug>false</debug>
    <parameters>false</parameters>
  </configuration>
</plugin>
```

项目上线后就失效了，报错 500，提示匹配不上。

![image-20220802220259134](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202208022202330.png)

- 案例解析

上述配置显示关闭了 parameters 和 debug。我们可以开启这两个参数来编译，然后使用下面的命令来查看信息：

```
javap -verbose HelloWorldController.class
```

![image-20220802220424316](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202208022204379.png)

debug 参数开启的部分信息就是 LocalVaribleTable，而 paramters 参数开启的信息就是 MethodParameters。观察它们的信息，你会发现它们都含有参数名 name。

如果关闭这两个参数，则 name 这个名称自然就没有了。如果 @RequestParam 中又没有指定名称，那么 Spring 此时还能找到解析的方法么？

这里我们可以顺带说下 Spring 解析请求参数名称的过程，参考代码 AbstractNamedValueMethodArgumentResolver#updateNamedValueInfo：

```java
private NamedValueInfo updateNamedValueInfo(
    MethodParameter parameter, NamedValueInfo) {
    String name = info.name;
    if (info.name.isEmpty()) {
        name = parameter.getParameterName();
        if (name == null) {
            throw new IllegalArgumentException("Name for argument type ["
                + parameter.getNestedParameterType().getName()
                + "] not available, and parameter name information not found in class file either.");
        }
    }
    String defaultValue = (ValueConstants.DEFAULT_NONE.equals(info.defaultValue)
                           ? null : info.defaultValue);
    return new NamedValueInfo(name, info.required, defaultValue);
}
```

其中 NamedValueInfo 的 name 为 @RequestParam 指定的值。很明显，在本案例中，为 null。

所以这里我们就会尝试调用 parameter.getParameterName() 来获取参数名作为解析请求参数的名称。当参数名不存在，@RequestParam 也没有指明，自然就无法决定到底要用什么名称去获取请求参数，所以就会报本案例的错误。

- 问题修正

模拟出了问题是如何发生的，我们自然可以通过开启这两个参数让其工作起来。但是思考这两个参数的作用，很明显，它可以让我们的程序体积更小，所以很多项目都会青睐去关闭这两个参数。

所以最好的修正方式是在 @RequestParam 中指定请求参数名。具体修改如下：

```java
@RequestParam("name") String name
```

另外，本案例围绕的都是 @RequestParam，其实 @PathVarible 也有一样的问题。

**案例 3：未考虑参数是否可选**

```java
@RequestMapping(path = "/hi4", method = RequestMethod.GET)
public String hi4(@RequestParam("name") String name, 
                  @RequestParam("address") address) {
    return name + ":" + address;
}
```

在访问 http://localhost:8080/hi4?name=xiaoming&address=beijing 时并不会出问题，但是一旦用户仅仅使用 name 做请求（即 http://localhost:8080/hi4?name=xiaoming ）时，则会直接报错如下：

![image-20220803214049384](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202208032140535.png)

既然不存在 address，address 应该设置为 null，而不应该是直接报错不是么？接下来我们就分析下。

- 案例解析

按注解名（@RequestParam）来确定解析发生的位置是在 RequestParamMethodArgumentResolver 中。接下来我们看下 RequestParamMethodArgumentResolver 对参数解析的一些关键操作，参考其父类方法 AbstractNamedValueMethodArgumentResolver#resolveArgument：

```java
public final Object resolveArgument(
    MethodParameter parameter, @Nullable ModelAndViewContainer mavContainer,
    NativeWebRequest webRequest, @Nullable WebDataBinderFactory binderFactory)
    throws Exception {
    NamedValueInfo namedValueInfo = getNamedValueInfo(parameter);
    MethodParameter nestedParameter = parameter.nestedIfOptional();
    //省略其他非关键代码
    //获取请求参数
    Object arg = resolveName(resolvedName.toString(), nestedParameter, webRequest);
    if (arg == null) {
        if (namedValueInfo.defaultValue != null) {
            arg = resolveStringValue(namedValueInfo.defaultValue);
        } else if (namedValueInfo.required && !nestedParameter.isOptional()) {
            handleMissingValue(namedValueInfo.name, nestedParameter, webRequest);
        }
        arg = handleNullValue(namedValueInfo.name, 
                              arg, nestedParameter.getNestedParameterType());
    }
    //省略后续代码：类型转化等工作
    return arg;
}
```

当缺少请求参数的时候，通常会按照以下几个步骤进行处理。

1. 查看 namedValueInfo 的默认值，如果存在则使用它；

2. 在 @RequestParam 没有指明默认值时，会查看这个参数是否必须，如果必须，则按错误处理；

   我们可以通过 MethodParameter#isOptional 方法看下可选的具体含义：

   ```java
   public boolean isOptional() {
       return (getParameterType() == Optional.class || hasNullableAnnotation() ||
               (KotlinDetector.isKotlinReflectPresent() &&
                KotlinDetector.isKotlinType(getContainingClass()) &&
                KotlinDelegate.isOptional(this)));
   }
   ```

   在不使用 Kotlin 的情况下，所谓可选，就是参数的类型为 Optional，或者任何标记了注解名为 Nullable 且 RetentionPolicy 为 RUNTIM 的注解。

3. 如果不是必须，则按 null 去做具体处理；

- 问题修正

通过案例解析，我们很容易就能修正这个问题，就是让参数有默认值或为非可选即可，具体方法包含以下几种。

1. 设置 @RequestParam 的默认值

```java
@RequestParam(value = "address", defaultValue = "no address") String address
```

2. 设置 @RequestParam 的 required 值

```java
@RequestParam(value = "address", required = false) String address)
```

3. 标记任何名为 Nullable 且 RetentionPolicy 为 RUNTIME 的注解

```java
//org.springframework.lang.Nullable 可以
//edu.umd.cs.findbugs.annotations.Nullable 可以
@RequestParam(value = "address") @Nullable String address
```

4. 修改参数类型为 Optional

```java
@RequestParam(value = "address") Optional address
```

**案例 4：请求参数格式错误**

当我们使用 Spring URL 相关的注解，会发现 Spring 是能够完成自动转化的。例如在下面的代码中，age 可以被直接定义为 int 这种基本类型（Integer 也可以）。

```java
@RequestMapping(path = "/hi5", method = RequestMethod.GET)
public String hi5(@RequestParam("name") String name, @RequestParam("age") int age) {
    return name + " is " + age + " years old";
}
```

那 Spring 支持日期类型的转化吗？

```java
@RequestMapping(path = "/hi6", method = RequestMethod.GET)
public String hi6(@RequestParam("Date") Date date) {
    return "date is " + date ;
}
```

我们使用符合日期格式的 URL 来访问，例如
http://localhost:8080/hi6?date=2021-5-1 20:26:53，我们会发现 Spring 并不能完成转化，而是报错如下：

```
Failed to convert value of type 'java.lang.String' to required type 'java.util.Date
```

- 案例解析

不管是使用 @PathVarible 还是 @RequetParam，我们一般解析出的结果都是一个 String 或 String 数组。使用 @RequetParam 解析的关键代码参考 RequestParamMethodArgumentResolver#resolveName 方法：

```java
@Nullable
protected Object resolveName(String name, MethodParameter parameter, 
                             NativeWebRequest request) throws Exception {
    //省略其他非关键代码
    if (arg == null) {
        String[] paramValues = request.getParameterValues(name);
        if (paramValues != null) {
            arg = (paramValues.length == 1 ? paramValues[0] : paramValues);
        }
    }
    return arg;
}
```

该方法最终给上层调用者返回的是单个 String 或者 String 数组。

对于 age 而言，最终找出的转化器是 StringToNumberConverterFactory。而对于 Date 型的 Date 变量，在本案例中，最终找到的是 ObjectToObjectConverter。它的转化过程参考下面的代码：

```java
public Object convert(@Nullable Object source, 
                      TypeDescriptor sourceType, TypeDescriptor targetType) {
    if (source == null) {
        return null;
    }
    Class<?> sourceClass = sourceType.getType();
    Class<?> targetClass = targetType.getType();
    //根据源类型去获取构建出目标类型的方法：可以是工厂方法（例如 valueOf、from 方法）也可以
    Member member = getValidatedMember(targetClass, sourceClass);
    try {
        if (member instanceof Method) {
            //如果是工厂方法，通过反射创建目标实例
        } else if (member instanceof Constructor) {
            //如果是构造器，通过反射创建实例
            Constructor<?> ctor = (Constructor<?>) member;
            ReflectionUtils.makeAccessible(ctor);
            return ctor.newInstance(source);
        }
    } catch (InvocationTargetException ex) {
        throw new ConversionFailedException(
            sourceType, targetType, source, ex.getTargetException());
    } catch (Throwable ex) {
        throw new ConversionFailedException(sourceType, targetType, source, ex);
    }
}
```

所以对于 Date 而言，最终调用的是下面的 Date 构造器：

```java
public Date(String s) {
    this(parse(s));
}
```

然而，我们传入的 2021-5-1 20:26:53 虽然确实是一种日期格式，但用来作为 Date 构造器参数是不支持的，最终报错，并被上层捕获，转化为 ConversionFailedException 异常。

- 问题修正

1. 使用 Date 支持的格式

```
http://localhost:8080/hi6?date=Sat, 12 Aug 1995 13:30:00 GMT
```

2. 使用好内置格式转化器

在 Spring 中，要完成 String 对于 Date 的转化，ObjectToObjectConverter 并不是最好的转化器。我们可以使用更强大的 AnnotationParserConverter。在 Spring 初
始化时，会构建一些针对日期型的转化器，即相应的一些 AnnotationParserConverter 的实例。但是为什么有时候用不上呢？

这是因为 AnnotationParserConverter 有目标类型的要求。参考 FormattingConversionService#addFormatterForFieldAnnotation 方法的调试试图：

![image-20220803224321984](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202208032243112.png)

这是适应于 String 到 Date 类型的转化器 AnnotationParserConverter 实例的构造过程，其需要的 annotationType 参数为 DateTimeFormat。

为了使用这个转化器，我们可以使用 @DateTimeFormat 并提供合适的格式。

```java
@DateTimeFormat(pattern="yyyy-MM-dd HH:mm:ss") Date date
```

# 10 | Spring Web Header 解析常见错误

虽然 Spring 对于 Header 的解析，大体流程和 URL 相同，但是 Header 本身具有自己的特点。例如，Header 不像 URL 只能出现在请求中。所以，Header 处理相关的错误和 URL 又不尽相同。接下来我们看看具体的案例。

**案例 1：接受 Header 使用错 Map 类型**

在 Spring 中解析 Header 时，我们在多数场合中是直接按需解析的。例如，我们想使用一个名为 myHeaderName 的 Header，我们会书写代码如下：

```java
@RequestMapping(path = "/hi", method = RequestMethod.GET)
public String hi(@RequestHeader("myHeaderName") String name) {
    //省略 body 处理
}
```

但是假设我们需要解析的 Header 很多时，按照上面的方式很明显会使得参数越来越多。在这种情况下，我们一般都会使用 Map 去把所有的 Header 都接收到，然后直接对 Map 进行处理。于是我们可能会写出下面的代码：

```java
@RequestMapping(path = "/hi1", method = RequestMethod.GET)
public String hi1(@RequestHeader() Map map) {
    return map.toString();
}
```

然后我们按如下方式请求该接口：

```
GET http://localhost:8080/hi1
myheader: h1
myheader: h2
```

会发现返回的结果并不能将这两个值如数返回，返回结果如下：

```
{myheader=h1, host=localhost:8080, connection=Keep-Alive, user-agent=Apache-HttpClient/4.5.12 (Java/11.0.6), accept-encodeing=gzip,default}
```

- 案例解析

对于一个多值的 Header，在实践中，通常有两种方式来传递，一种是采用下面的方式：

```
Key: value1,value2
```

而另外一种方式就是我们上面提到的格式：

```
Key:value1
Key:value2
```

对于方式 1，我们使用 Map 接口自然不成问题。但是如果使用的是方式 2，我们使用 Map 接口就不能拿到所有的值。

对于一个 Header 的解析，主要有两种方式，分别实现在 RequestHeaderMethodArgumentResolver 和 RequestHeaderMapMethodArgumentResolver 中，它们都继承于 AbstractNamedValueMethodArgumentResolver，但是应用的场景不同，我们可以对比下它们的 supportsParameter()，来对比它们适合的场景：

![image-20220804214914255](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202208042149431.png)

在上图中，左边是 RequestHeaderMapMethodArgumentResolver 的方法。通过比较可以发现，对于一个标记了 @RequestHeader 的参数，如果它的类型是 Map，则使用 RequestHeaderMapMethodArgumentResolver，否则一般使用的是 RequestHeaderMethodArgumentResolver。

在本案例中，参数类型定义为 Map，所以使用的自然是 RequestHeaderMapMethodArgumentResolver。

接下来，我们继续查看它是如何解析 Header 的，关键代码参考 resolveArgument()：

```java
@Override
public Object resolveArgument(
    MethodParameter parameter, @Nullable ModelAndViewContainer mavContainer,
    NativeWebRequest webRequest, @Nullable WebDataBinderFactory binderFactory)
    throws Exception {
    Class<?> paramType = parameter.getParameterType();
    if (MultiValueMap.class.isAssignableFrom(paramType)) {
        // ...
    } else {
        Map<String, String> result = new LinkedHashMap<>();
        for (Iterator<String> iterator = webRequest.getHeaderNames(); iterator.hasNext();) {
            String headerName = iterator.next();
            //只取了一个“值”
            String headerValue = webRequest.getHeader(headerName);
            if (headerValue != null) {
                result.put(headerName, headerValue);
            }
        }
        return result;
    }
}
```

本案例并不是 MultiValueMap，所以会走入 else 分支。这个分支首先会定义一个 LinkedHashMap，然后将请求一一放置进去，并返回。当一个请求出现多个同名 Header 时，我们只要匹配上任何一个即立马返回。

> 其实换一个角度思考这个问题，毕竟前面已经定义的接收类型是 LinkedHashMap，它的 Value 的泛型类型是 String，也不适合去组织多个值的情况。

- 问题修正

在 RequestHeaderMapMethodArgumentResolver 的 resolveArgument() 中，假设我们的参数类型是 MultiValueMap。

```java
@Override
public Object resolveArgument(
    MethodParameter parameter, @Nullable ModelAndViewContainer mavContainer,
    NativeWebRequest webRequest, @Nullable WebDataBinderFactory binderFactory)
    throws Exception {
    Class<?> paramType = parameter.getParameterType();
    if (MultiValueMap.class.isAssignableFrom(paramType)) {
        MultiValueMap<String, String> result;
        if (HttpHeaders.class.isAssignableFrom(paramType)) {
            result = new HttpHeaders();
        } else {
            result = new LinkedMultiValueMap<>();
        }
        for (Iterator<String> iterator = webRequest.getHeaderNames(); iterator.hasNext();) {
            String headerName = iterator.next();
            String[] headerValues = webRequest.getHeaderValues(headerName);
            if (headerValues != null) {
                for (String headerValue : headerValues) {
                    result.add(headerName, headerValue);
                }
            }
        }
        return result;
    } else {
        //...
    }
}
```

我们一般会创建一个 LinkedMultiValueMap，然后使用下面的语句来获取 Header 的值并添加到 Map 中去：

```java
String[] headerValues = webRequest.getHeaderValues(headerName)
```

另外假设我们定义的是 HttpHeaders（也是一种 MultiValueMap），我们会直接创建一个 HttpHeaders 来存储所有的 Header。

有了上面的解析，我们可以采用以下两种方式来修正这个问题：

```java
//方式 1
@RequestHeader() MultiValueMap map
//方式 2
@RequestHeader() HttpHeaders map
```

**案例 2：错认为 Header 名称首字母可以一直忽略大小写**

在 HTTP 协议中，Header 的名称是无所谓大小写的。我们可以验证下。

```java
@RequestMapping(path = "/hi2", method = RequestMethod.GET)
public String hi2(@RequestHeader("MyHeader") String myHeader, 
                  @RequestHeader MultiValueMap map) {
    return myHeader + " compare with : " + map.get("MyHeader");
}
```

然后，我们使用下面的请求来测试这个接口：

```
GET http://localhost:8080/hi2
myheader: myheadervalue
```

得出下面的结果：

```
myheadervalue compare with : null
```

综合来看，直接获取 Header 是可以忽略大小写的，但是如果从接收过来的 Map 中获取 Header 是不能忽略大小写的。

- 案例解析

对于"@RequestHeader("MyHeader") String myHeader"的定义，Spring 使用的是 RequestHeaderMethodArgumentResolver 来做解析。解析的方法参考 RequestHeaderMethodArgumentResolver#resolveName：

```java
protected Object resolveName(String name, MethodParameter parameter, 
                             NativeWebRequest request) throws Exception {
    String[] headerValues = request.getHeaderValues(name);
    if (headerValues != null) {
        return (headerValues.length == 1 ? headerValues[0] : headerValues);
    } else {
        return null;
    }
}
```

上述方法调用了"request.getHeaderValues(name)"，可以找到查找 Header 的最根本方法，即 org.apache.tomcat.util.http.ValuesEnumerator#findNext：

```java
private void findNext() {
    next=null;
    for(; pos< size; pos++ ) {
        MessageBytes n1=headers.getName(pos);
        if( n1.equalsIgnoreCase( name )) {
            next=headers.getValue( pos );
            break;
        }
    }
    pos++;
}
```

在上述方法中，name 即为查询的 Header 名称。可以看出这里是忽略大小写的。

- 问题修正

我们使用 HTTP Headers 来接收请求，其构造器代码如下:

```java
public HttpHeaders() {
    this(CollectionUtils.toMultiValueMap(new LinkedCaseInsensitiveMap<>(8, Locale.ENGLISH)));
}
```

它使用的是 LinkedCaseInsensitiveMap，而不是普通的 LinkedHashMap。所以是可以忽略大小写的，我们不妨这样修正：

```java
@RequestMapping(path = "/hi2", method = RequestMethod.GET)
public String hi2(@RequestHeader("MyHeader") String myHeader, 
                  @RequestHeader HttpHeaders map) {
    return myHeader + " compare with : " + map.get("MyHeader");
}
```

通过这个案例，我们可以看出：在实际使用时，虽然 HTTP 协议规范可以忽略大小写，但不是所有框架提供的接口方法都是可以忽略大小写的。

**案例 3：试图在 Controller 中随意自定义 CONTENT_TYPE 等**

使用 Spring Boot 基于 Tomcat 内置容器的开发中，存在下面这样一段代码去设置两个 Header：

```java
@RequestMapping(path = "/hi3", method = RequestMethod.GET)
public String hi3(HttpServletResponse httpServletResponse){
    httpServletResponse.addHeader("myheader", "myheadervalue");
    httpServletResponse.addHeader(HttpHeaders.CONTENT_TYPE, "application/json");
    return "ok";
}
```

运行程序后访问 GET http://localhost:8080/hi3，我们会得到如下结果：

```http
GET http://localhost:8080/hi3

HTTP/1.1 200
myheader: myheadervalue
Content-Type: text/plain;charset=UTF-8
Content-Length: 2
Date: Wed, 17 Mar 2021 08:59:56 GMT
Keep-Alive: timeout=60
Connection: keep-alive
```

可以看到 myHeader 设置成功了，但是 Content-Type 并没有设置成我们想要的"application/json"，而是"text/plain;charset=UTF-8"。为什么会出现这种错误？

- 案例解析

首先我们来看下在 Spring Boot 使用内嵌 Tomcat 容器时，尝试添加 Header 会执行哪些关键步骤。

第一步，我们可以查看 org.apache.catalina.connector.Response#addHeader 方法，代码如下：

```java
private void addHeader(String name, String value, Charset charset) {
    //省略其他非关键代码
    char cc = name.charAt(0);
    if (cc == 'C' || cc == 'c') {
        //判断是不是 Content-Type，如果是不要把这个 Header 添加到 org.apache.coyote.Response
        if (checkSpecialHeader(name, value))
            return;
    }
    getCoyoteResponse().addHeader(name, value, charset);
}
```

第二步，在案例代码返回 ok 后，我们需要对返回结果进行处理，执行方法为 RequestResponseBodyMethodProcessor#handleReturnValue，关键代码如下：

```java
@Override
public void handleReturnValue(@Nullable Object returnValue, 
                              MethodParameter returnType,
                              ModelAndViewContainer mavContainer, 
                              NativeWebRequest webRequest)
    throws IOException, HttpMediaTypeNotAcceptableException, HttpMessageNotWritableException {
    mavContainer.setRequestHandled(true);
    ServletServerHttpRequest inputMessage = createInputMessage(webRequest);
    ServletServerHttpResponse outputMessage = createOutputMessage(webRequest);
    //对返回值(案例中为“ok”)根据返回类型做编码转化处理
    writeWithMessageConverters(returnValue, returnType, inputMessage, outputMes
}
```

writeWithMessageConverters 会根据返回值及类型做转化，同时也会做一些额外的事情。它的一些关键实现步骤参考下面几步：

1. 决定用哪一种 MediaType 返回
2. 选择消息转化器并完成转化

最终，本案例选择的是 StringHttpMessageConverter，在最终调用父类方法 AbstractHttpMessageConverter#write 执行转化时，会尝试添加 Content-Type。具体代码参考 AbstractHttpMessageConverter#addDefaultHeaders。

结合案例，参考代码，我们可以看出，我们使用的是 MediaType#TEXT_PLAIN 作为 Content-Type 的 Header，毕竟之前我们添加 Content-Type 这个 Header 并没有成功。最终运行结果也就不出意外了，即"Content-Type: text/plain;charset=UTF-8"。

通过案例分析，我们可以总结出，虽然我们在 Controller 设置了 Content-Type，但是它是一种特殊的 Header，所以在 Spring Boot 基于内嵌 Tomcat 开发时并不一定能设置成功，最终返回的 Content-Type 是根据实际的返回值及类型等多个因素来决定的。

- 问题修正

1. 修改请求中的 Accept 头，约束返回类型

```
GET http://localhost:8080/hi3
Accept:application/json
```

2. 标记返回类型

```java
@RequestMapping(path = "/hi3", method = RequestMethod.GET, produces = {"application/json"})
```

上述两种方式，一个修改了 getAcceptableMediaTypes 返回值，一个修改了 getProducibleMediaTypes，这样就可以控制最终协商的结果为 JSON 了。从而影响后续的执行结果

# 11 | Spring Web Body 转化常见错误

在 Spring 中，对于 Body 的处理很多是借助第三方编解码器来完成的。例如常见的 JSON 解析，Spring 都是借助于 Jackson、Gson 等常见工具来完成。

**案例 1：No converter found for return value of type**

在直接用 Spring MVC 而非 Spring Boot 来编写 Web 程序时，我们基本都会遇到 "No converter found for return value of type" 这种错误。

例如下面这段代码：

```java
//定义的数据对象
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Student {
    private String name;
    private Integer age;
}

//定义的 API 借口
@RestController
public class HelloController {
    @GetMapping("/hi1")
    public Student hi1() {
        return new Student("xiaoming", Integer.valueOf(12));
    }
}
```

然后，pom.xml 关键依赖如下：

```xml
<dependency>
    <groupId>org.springframework</groupId>
    <artifactId>spring-webmvc</artifactId>
    <version>5.2.3.RELEASE</version>
</dependency>
```

当我们运行起程序，执行测试代码，就会报错如下：

![image-20220808220546766](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202208082205006.png)

- 案例解析

当我们的请求到达 Controller 层后，我们获取到了一个对象，即案例中的 new Student("xiaoming", Integer.valueOf(12))，那么这个对象应该怎么返回给客户端呢？

此时就需要一个决策，我们可以先找到这个决策的关键代码所在，参考方法 AbstractMessageConverterMethodProcessor#writeWithMessageConverters：

```java
HttpServletRequest request = inputMessage.getServletRequest();
List<MediaType> acceptableTypes = getAcceptableMediaTypes(request);
List<MediaType> producibleTypes = getProducibleMediaTypes(
    request, valueType, targetType);
if (body != null && producibleTypes.isEmpty()) {
    throw new HttpMessageNotWritableException(
        "No converter found for return value of type: " + valueType);
}
List<MediaType> mediaTypesToUse = new ArrayList<>();
for (MediaType requestedType : acceptableTypes) {
    for (MediaType producibleType : producibleTypes) {
        if (requestedType.isCompatibleWith(producibleType)) {
            mediaTypesToUse.add(
                getMostSpecificMediaType(requestedType, producibleType));
        }
    }
}
```

简要分析下上述代码的基本逻辑：

1. 查看请求的头中是否有 ACCET 头，如果没有则可以使用任何类型；
2. 查看当前针对返回类型（即 Student 实例）可以采用的编码类型；
3. 取上面两步获取结果的交集来决定用什么方式返回。

那么当前可采用的编码类型是怎么决策出来的呢？

假设当前没有显式指定返回类型（例如给 GetMapping 指定 produces 属性），那么则会遍历所有已经注册的 HttpMessageConverter 查看是否支持当前类型，从而最终返回所有支持的类型。（AbstractMessageConverterMethodProcessor#getProducibleMediaTypes）

那么这些 MessageConverter 是怎么注册过来的？

在 Spring MVC（非 Spring Boot）启动后，我们都会构建 RequestMappingHandlerAdapter 类型的 Bean 来负责路由和处理请求。具体而言，当我们使用`<mvc:annotation-driven/>`时，我们会通过 AnnotationDrivenBeanDefinitionParser 来构建这个 Bean。而在它的构建过程中，会决策出以后要使用哪些 HttpMessageConverter，相关代码参考 AnnotationDrivenBeanDefinitionParser#getMessageConverters。

这里我们会默认使用一些编解码器，例如 StringHttpMessageConverter，但是像 JSON、XML 等类型，若要加载编解码，则需要 jackson2Present、gsonPresent 等变量为 true。gsonPresent 何时为 true，参考下面的关键代码行：

```java
gsonPresent = ClassUtils.isPresent("com.google.gson.Gson", classLoader);
```

由此可见，并没有任何 JSON 相关的编解码器。而针对 Student 类型的返回对象，上面的这些编解码器又不符合要求，所以最终走入了下面的代码行：

```java
if (body != null && producibleTypes.isEmpty()) {
    throw new HttpMessageNotWritableException(
        "No converter found for return value of type: " + valueType);
}
```

- 问题修正

```xml
<dependency>
    <groupId>com.google.code.gson</groupId>
    <artifactId>gson</artifactId>
    <version>2.8.6</version>
</dependency>
```

**案例 2：变动地返回 Body**

案例 1 让我们解决了解析问题，那随着不断实践，我们可能还会发现在代码并未改动的情况下，返回结果不再和之前相同了。例如我们看下这段代码：

```java
@RestController
public class HelloController {
    @PostMapping("/hi2")
    public Student hi2(@RequestBody Student student) {
        return student;
    }
}
```

我们使用下面的测试请求进行测试：

```http
POST http://localhost:8080/springmvc3_war/app/hi2
Content-Type: application/json
{
"name": "xiaoming"
}
```

得到以下结果：

```json
{
    "name": "xiaoming"
}
```

但是随着项目的推进，在代码并未改变时，我们可能会返回以下结果：

```json
{
    "name": "xiaoming",
    "age": null
}
```

即当 age 取不到值，开始并没有序列化它作为响应 Body 的一部分，后来又序列化成 null 作为 Body 返回了。在什么情况下会如此？

- 案例解析

在后续的代码开发中，我们直接依赖或者间接依赖了新的 JSON 解析器，例如下面这种方式就依赖了 Jackson：

```xml
<dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
    <version>2.9.6</version>
</dependency>
```

当存在多个 Jackson 解析器时，我们的 Spring MVC 会使用哪一种呢？

```java
if (jackson2Present) {
    Class<?> type = MappingJackson2HttpMessageConverter.class;
    RootBeanDefinition jacksonConverterDef = createConverterDefinition(type, source);
    GenericBeanDefinition jacksonFactoryDef = createObjectMapperFactoryDefinition(source);
    jacksonConverterDef.getConstructorArgumentValues()
        .addIndexedArgumentValue(0, jacksonFactoryDef);
    messageConverters.add(jacksonConverterDef);
} else if (gsonPresent) {
    messageConverters.add(
        createConverterDefinition(GsonHttpMessageConverter.class, source));
}
```

从上述代码可以看出，Jackson 是优先于 Gson 的。所以我们的程序不知不觉已经从 Gson 编解码切换成了 Jackson。

针对本案例中序列化值为 null 的字段的行为而言，我们可以分别看下它们的行为是否一致。

1. 对于 Gson 而言：

GsonHttpMessageConverter 默认使用 new Gson() 来构建 Gson，它的构造器中指明了相关配置：

```java
public Gson() {
    this(Excluder.DEFAULT, FieldNamingPolicy.IDENTITY,
         Collections.<Type, InstanceCreator<?>>emptyMap(), DEFAULT_SERIALIZE_NULLS,
         DEFAULT_COMPLEX_MAP_KEYS, DEFAULT_JSON_NON_EXECUTABLE, DEFAULT_ESCAPE_HTML,
         DEFAULT_PRETTY_PRINT, DEFAULT_LENIENT, DEFAULT_SPECIALIZE_FLOAT_VALUES,
         LongSerializationPolicy.DEFAULT, null, DateFormat.DEFAULT, DateFormat.DEFAULT,
         Collections.<TypeAdapterFactory>emptyList(), Collections.<TypeAdapterFactory>emptyList(),
         Collections.<TypeAdapterFactory>emptyList());
}
```

从 DEFAULT_SERIALIZE_NULLS 可以看出，它默认是不序列化 null 的。

> 这个名字怎么看也不像是“默认是不序列化 null”。

2. 对于 Jackson 而言：

MappingJackson2HttpMessageConverter 使用"Jackson2ObjectMapperBuilder.json().build()"来构建 ObjectMapper，它默认只显式指定了下面两个配置：

```
MapperFeature.DEFAULT_VIEW_INCLUSION
DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES
```

Jackson 默认对于 null 的处理是做序列化的。

- 问题修正

这里可以按照以下方式进行修改：

```java
@Data
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class Student {
    private String name;
    //或直接加在 age 上@JsonInclude(JsonInclude.Include.NON_NULL)
    private Integer age;
}
```

上述修改方案虽然看起来简单，但是假设有很多对象如此，万一遗漏了怎么办呢？所以可以从全局角度来修改，修改的关键代码如下：

```
//ObjectMapper mapper = new ObjectMapper();
mapper.setSerializationInclusion(Include.NON_NULL);
```

在非 Spring Boot 程序中，可以按照下面这种方式来修改：

```java
@RestController
public class HelloController {
    public HelloController(RequestMappingHandlerAdapter requestMappingHandlerAdapter) {
        List<HttpMessageConverter<?>> messageConverters =
            requestMappingHandlerAdapter.getMessageConverters();
        for (HttpMessageConverter<?> messageConverter : messageConverters) {
            if(messageConverter instanceof MappingJackson2HttpMessageConverter ) {
                (((MappingJackson2HttpMessageConverter)messageConverter).getObjectMapper())
                .setSerializationInclusion(JsonInclude.Include.NON_NULL);
            }
        }
    }
    //省略其他非关键代码
}
```

我们用自动注入的方式获取到 RequestMappingHandlerAdapter，然后找到 Jackson 解析器，进行配置即可。

**案例 3：Required request body is missing**

为了查询问题方便，在请求过来时，自定义一个 Filter 来统一输出具体的请求内容，关键代码如下：

```java
public class ReadBodyFilter implements Filter {
    //省略其他非关键代码
    @Override
    public void doFilter(ServletRequest request,
                         ServletResponse response, FilterChain chain)
        throws IOException, ServletException {
        String requestBody = IOUtils.toString(request.getInputStream(), "utf-8");
        System.out.println("print request body in filter:" + requestBody);
        chain.doFilter(request, response);
    }
}
```

然后，我们可以把这个 Filter 添加到 web.xml 并配置如下：

```xml
<filter>
    <filter-name>myFilter</filter-name>
    <filter-class>com.puzzles.ReadBodyFilter</filter-class>
</filter>
<filter-mapping>
    <filter-name>myFilter</filter-name>
    <url-pattern>/app/*</url-pattern>
</filter-mapping>
```

再测试下 Controller 层中定义的接口：

```java
@PostMapping("/hi3")
public Student hi3(@RequestBody Student student) {
    return student;
}
```

请求的 Body 确实在请求中输出了，但是后续的操作直接报错了，错误提示：Required request body is missing。

- 案例解析

有 Body，但是 Body 本身代表的流已经被前面读取过了。在这种情况下，作为一个普通的流，已经没有数据可以供给后面的转化器来读取了。

查阅请求 Body 转化的相关代码（参考 RequestResponseBodyMethodProcessor#readWithMessageConverters）。

- 问题修正

定义一个 RequestBodyAdviceAdapter 的 Bean：

```java
@ControllerAdvice
public class PrintRequestBodyAdviceAdapter extends RequestBodyAdviceAdapter {
    @Override
    public boolean supports(
        MethodParameter methodParameter, Type type, 
        Class<? extends HttpMessageConverter<?>> aClass) {
        return true;
    }
    @Override
    public Object afterBodyRead(
        Object body, HttpInputMessage inputMessage, MethodParameter parameter, 
        Type targetType, Class<? extends HttpMessageConverter<?>> converterType) {
        System.out.println("print request body in advice:" + body);
        return super.afterBodyRead(body, inputMessage, parameter, targetType, converterType);
    }
}
```

那么它是如何工作起来的呢？我们可以查看下面的代码（参考 AbstractMessageConverterMethodArgumentResolver#readWithMessageConverters）。

# 12｜Spring Web 参数验证常见错误

参数检验是我们在 Web 编程时经常使用的技术之一，它帮助我们完成请求的合法性校验，可以有效拦截无效请求，从而达到节省系统资源、保护系统的目的。

**案例 1：对象参数校验失效**

当开发一个学籍管理系统时，我们会提供了一个 API 接口去添加学生的相关信息，其对象定义参考下面的代码：

```java
import lombok.Data;
import javax.validation.constraints.Size;
@Data
public class Student {
    @Size(max = 10)
    private String name;
    private short age;
}
```

这里我们使用了 @Size(max = 10) 给学生的姓名做了约束（最大为 10 字节），以拦截姓名过长的学生信息的添加。定义完对象后，我们再定义一个 Controller 去使用它，使用方法如下：

```java
@RestController
@Slf4j
@Validated
public class StudentController {
    @RequestMapping(path = "students", method = RequestMethod.POST)
    public void addStudent(@RequestBody Student student) {
        log.info("add new student: {}", student.toString());
        //省略业务代码
    }
}
```

调用该接口：

```http
POST http://localhost:8080/students
Content-Type: application/json
{
"name": "this_is_my_name_which_is_too_long",
"age": 10
}
```

会发现，使用上述代码构建的 Web 服务并没有做任何拦截。

- 案例解析

首先，我们来看下 RequestBody 接受对象校验发生的位置和条件。下图基于 Spring Boot 来分析：

![image-20220809205623021](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202208092056328.png)

1. InvocableHandlerMethod#invokeForRequest

```java
public Object invokeForRequest(
    NativeWebRequest request, @Nullable ModelAndViewContainer mavContainer,
    Object... providedArgs) throws Exception {
    //根据请求内容和方法定义获取方法参数实例
    Object[] args = getMethodArgumentValues(request, mavContainer, providedArgs);
    if (logger.isTraceEnabled()) {
        logger.trace("Arguments: " + Arrays.toString(args));
    }
    //携带方法参数实例去“反射”调用方法
    return doInvoke(args);
}
```

具体 getMethodArgumentValues() 如何获取方法调用参数，可以参考 addStudent 的方法定义，我们需要从当前的请求（NativeWebRequest ）中构建出 Student 这个方法参数的实例。

2. 如何构建出这个方法参数实例？

Spring 内置了相当多的HandlerMethodArgumentResolver，参考下图：

![image-20220809213245779](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202208092132100.png)

当试图构建出一个方法参数时，会遍历所有支持的解析器（Resolver）以找出适合的解析器，查找代码参考 HandlerMethodArgumentResolverComposite#getArgumentResolver。

对于 student 参数而言，它被标记为 @RequestBody，当遍历到 RequestResponseBodyMethodProcessor 时就会匹配上。（参考RequestResponseBodyMethodProcessor#supportsParameter）

3. 执行 HandlerMethodArgumentResolver#resolveArgument 

它首先会根据当前的请求（NativeWebRequest）组装出 Student 对象并对这个对象进行必要的校验，校验的执行参考 AbstractMessageConverterMethodArgumentResolver#validateIfApplicable：

```java
protected void validateIfApplicable(WebDataBinder binder, MethodParameter parameter) {
    Annotation[] annotations = parameter.getParameterAnnotations();
    for (Annotation ann : annotations) {
        Validated validatedAnn = AnnotationUtils.getAnnotation(ann, Validated.class);
        //判断是否需要校验
        if (validatedAnn != null || ann.annotationType().getSimpleName().startsWith("Valid")) {
            Object hints = (validatedAnn != null ? 
                            validatedAnn.value() : AnnotationUtils.getValue(ann));
            Object[] validationHints = (hints instanceof Object[] ? 
                                        (Object[]) hints : new Object[] {hints});
            //执行校验
            binder.validate(validationHints);
            break;
        }
    }
}
```

如上述代码所示，要对 student 实例进行校验（执行 binder.validate(validationHints) 方法），必须匹配下面两个条件的其中之一：

```
1. 标记了 org.springframework.validation.annotation.Validated 注解；
2. 标记了其他类型的注解，且注解名称以 Valid 关键字开头；
```

- 问题修正

1. 标记 @Validated

```java
public void addStudent(@Validated @RequestBody Student student)
```

2. 标记 @Valid 关键字开头的注解

```java
public void addStudent(@Valid @RequestBody Student student)
```

另外，我们也可以自定义一个以 Valid 关键字开头的注解，定义如下：

```java
@Retention(RetentionPolicy.RUNTIME)
public @interface ValidCustomized {
}
```

定义完成后，将它标记给 student 参数对象，关键代码行如下：

```java
public void addStudent(@ValidCustomized @RequestBody Student student)
```

注意 @ValidCustomized 注解要显式标记 @Retention(RetentionPolicy.RUNTIME)，否则校验仍不生效。

不显式标记 RetentionPolicy 时，默认使用的是RetentionPolicy.CLASS，而这种类型的注解信息虽然会被保留在字节码文件（.class）中，但在加载进 JVM 时就会丢失了。所以在运行时，依据这个注解来判断是否校验，肯定会失效。

**案例 2：嵌套校验失效**

学生可能还需要一个联系电话信息，所以我们可以定义一个 Phone 对象，然后关联上学生对象，代码如下：

```java
public class Student {
    @Size(max = 10)
    private String name;
    private short age;
    private Phone phone;
}

@Data
class Phone {
    @Size(max = 10)
    private String number;
}
```

当我们使用下面的请求测试，会发现这个校验约束并不生效。

```json
POST http://localhost:8080/students
Content-Type: application/json
{
"name": "xiaoming",
"age": 10,
"phone": {"number":"12306123061230612306"}
}
```

- 案例解析

关于 student 本身的 Phone 类型成员是否校验，是在校验过程中`binder.validate(validationHints)`决定的。

在校验执行时，首先会根据 Student 的类型定义找出所有的校验点，然后对 Student 对象实例执行校验，这个逻辑过程可以参考代码 ValidatorImpl#validate：

```java
@Override
public final <T> Set<ConstraintViolation<T>> validate(T object, Class<?>... groups) {
    //省略部分非关键代码
    Class<T> rootBeanClass = (Class<T>) object.getClass();
    //获取校验对象类型的“信息”（包含“约束”）
    BeanMetaData<T> rootBeanMetaData = beanMetaDataManager.getBeanMetaData(rootBeanClass);
    if ( !rootBeanMetaData.hasConstraints() ) {
        return Collections.emptySet();
    }
    //省略部分非关键代码
    //执行校验
    return validateInContext(validationContext, valueContext, validationOrder);
}
```

这里语句"beanMetaDataManager.getBeanMetaData(rootBeanClass)"根据 Student 类型组装出 BeanMetaData，BeanMetaData 即包含了需要做的校验（即Constraint）。

在组装 BeanMetaData 过程中，会根据成员字段是否标记了 @Valid 来决定（记录）这个字段以后是否做级联校验，参考代码
AnnotationMetaDataProvider#getCascadingMetaData：

```java
private CascadingMetaDataBuilder getCascadingMetaData(
    Type type, AnnotatedElement annotatedElement,
    Map<TypeVariable<?>, CascadingMetaDataBuilder> containerElementTypesCascadingMetaData) {
    return CascadingMetaDataBuilder.annotatedObject(
        type, 
        annotatedElement.isAnnotationPresent(Valid.class), 
        containerElementTypesCascadingMetaData,
        getGroupConversions(annotatedElement));
}
```

在上述代码中"annotatedElement.isAnnotationPresent( Valid.class )"决定了 CascadingMetaDataBuilder#cascading 是否为 true。如果是，则在后续做具体校验时，做级联校验，而级联校验的过程与宿主对象（即 Student）的校验过程大体相同，即先根据对象类型获取定义再来做校验。

- 问题修正

```java
@Valid
private Phone phone;
```

当修正完问题后，我们会发现校验生效了。而如果此时去调试修正后的案例代码，会看到 phone 字段 MetaData 信息中的 cascading 确实为 true 了，参考下图：

![image-20220811214620212](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202208112146736.png)

**案例 3：误解校验执行**

之前我们定义的学生对象的姓名要求是小于 10 字节的（即 @Size(max = 10)）。此时我们可能想完善校验，例如，我们希望姓名不能是空，此时你可能很容易想到去修改关键行代码如下：

```java
@Size(min = 1, max = 10)
private String name;
```

然后，我们以下面的 JSON Body 做测试：

```json
{
    "name": "",
    "age": 10,
    "phone": {"number":"12306"}
}
```

测试结果符合我们的预期，但是用下面的 JSON Body（去除 name 字段）做测试呢？

```json
{
    "age": 10,
    "phone": {"number":"12306"}
}
```

我们会发现校验失败了。

- 案例解析

其实 @Size 的 Javadoc 已经明确了这种情况，参考下图：

<img src="https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202208112156358.png" alt="image-20220811215626073" style="zoom: 33%;" />

我们也找到了完成 @Size 约束的执行方法，参考 SizeValidatorForCharSequence#isValid 方法：

```java
public boolean isValid(CharSequence charSequence, ConstraintValidatorContext constraintValidatorContext) {
    if (charSequence == null) {
        return true;
    }
    int length = charSequence.length();
    return length >= min && length <= max;
}
```

如代码所示，当字符串为 null 时，直接通过了校验，而不会做任何进一步的约束检查。

- 问题修正

```java
@NotEmpty
@Size(min = 1, max = 10)
private String name;
```

# 13 | Spring Web 过滤器使用常见错误（上）

在 Spring 编程中，我们主要就是配合使用 @ServletComponentScan 和 @WebFilter 这两个注解来构建过滤器。

**案例 1：@WebFilter 过滤器无法被自动注入**

假设我们要基于 Spring Boot 去开发一个学籍管理系统。为了统计接口耗时，可以实现一个过滤器如下：

```java
@WebFilter
@Slf4j
public class TimeCostFilter implements Filter {
    public TimeCostFilter() {
        System.out.println("construct");
    }
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) 
        throws IOException, ServletException {
        log.info("开始计算接口耗时");
        long start = System.currentTimeMillis();
        chain.doFilter(request, response);
        long end = System.currentTimeMillis();
        long time = end - start;
        System.out.println("执行时间(ms)：" + time);
    }
}
```

这个过滤器标记了 @WebFilter。所以在启动程序中，我们需要加上扫描注解（即@ServletComponentScan）让其生效，启动程序如下：

```java
@SpringBootApplication
@ServletComponentScan
@Slf4j
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
        log.info("启动成功");
    }
}
```

然后，我们提供了一个 StudentController 接口来供学生注册：

```java
@Controller
@Slf4j
public class StudentController {
    @PostMapping("/regStudent/{name}")
    @ResponseBody
    public String saveUser(String name) throws Exception {
        System.out.println("用户注册成功");
        return "success";
    }
}
```

上述程序完成后，你会发现一切按预期执行。但是假设有一天，我们可能需要把 TimeCostFilter 记录的统计数据输出到专业的度量系统（ElasticeSearch/InfluxDB 等）里面去，我们可能会添加这样一个 Service 类：

```java
@Service
public class MetricsService {
    @Autowired
    public TimeCostFilter timeCostFilter;
    //省略其他非关键代码
}
```

完成后你会发现，Spring Boot 都无法启动了：

```
***************************
APPLICATION FAILED TO START
***************************
Description:
Field timeCostFilter in com.spring.puzzle.web.filter.example1.MetricsService required a bean of type 'com.spring.puzzle.web.filter.example1.TimeCostFilter' that could not be found.
```

- 案例解析

本质上，过滤器被 @WebFilter 修饰后，TimeCostFilter 只会被包装为 FilterRegistrationBean，而 TimeCostFilter 自身，只会作为一个 InnerBean 被实例化，这意味着 TimeCostFilter 实例并不会作为 Bean 注册到 Spring 容器。

![image-20220812211946116](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202208122119327.png)

所以当我们想自动注入 TimeCostFilter 时，就会失败了。知道这个结论后，我们可以带着两个问题去理清一些关键的逻辑：

1. FilterRegistrationBean 是什么？它是如何被定义的？
2. TimeCostFilter 是怎么实例化，并和 FilterRegistrationBean 关联起来的？

我们先来看第一个问题：FilterRegistrationBean 是什么？它是如何定义的？

实际上，WebFilter 的全名是 javax.servlet.annotation.WebFilter，很明显，它并不属于 Spring，而是 Servlet 的规范。当 Spring Boot 项目中使用它时，Spring Boot 使用了 org.springframework.boot.web.servlet.FilterRegistrationBean 来包装 @WebFilter 标记的实例。从实现上来说，即 FilterRegistrationBean#Filter 属性就是 @WebFilter 标记的实例。

那么这个 FilterRegistrationBean 是如何定义的呢？我们先看下 @WebFilter 是如何工作起来的。使用 @WebFilter 时，Filter 被加载有两个条件：

1. 声明了 @WebFilter；
2. 在能被 @ServletComponentScan 扫到的路径之下。

这里我们直接检索对 @WebFilter 的使用，可以发现 WebFilterHandler 类使用了它，直接在 doHandle() 中加入断点，开始调试，执行调用栈如下：

![image-20220812213549257](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202208122135398.png)

从堆栈上，我们可以看出对 @WebFilter 的处理是在 Spring Boot 启动时，而处理的触发点是 ServletComponentRegisteringPostProcessor 这个类。它继承了 BeanFactoryPostProcessor 接口，实现对 @WebFilter、@WebListener、@WebServlet 的扫描和处理，其中对于 @WebFilter 的处理使用的就是上文中提到的WebFilterHandler。

最终，WebServletHandler 通过父类 ServletComponentHandler 的模版方法模式，处理了所有被 @WebFilter 注解的类，关键代码如下：

```java
public void doHandle(Map<String, Object> attributes, AnnotatedBeanDefinition beanDefinition,
                     BeanDefinitionRegistry registry) {
    BeanDefinitionBuilder builder = BeanDefinitionBuilder
        .rootBeanDefinition(FilterRegistrationBean.class);
    builder.addPropertyValue("asyncSupported", attributes.get("asyncSupported"));
    builder.addPropertyValue("dispatcherTypes", extractDispatcherTypes(attributes));
    builder.addPropertyValue("filter", beanDefinition);
    //省略其他非关键代码
    builder.addPropertyValue("urlPatterns", extractUrlPatterns(attributes));
    registry.registerBeanDefinition(name, builder.getBeanDefinition());
}
```

从这里，我们第一次看到了 FilterRegistrationBean。通过调试上述代码的最后一行，可以看到，最终我们注册的 FilterRegistrationBean，其名字就是我们定义的 WebFilter 的名字：

![image-20220812214151580](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202208122141771.png)

现在，我们接着看第二个问题：TimeCostFilter 何时被实例化？为什么它没有成为一个普通的 Bean?

关于这点，我们可以在 TimeCostFilter 的构造器中加个断点，然后使用调试的方式快速定位到它的初始化时机，这里我直接给出了调试截图：

![image-20220812214845284](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202208122148430.png)

在上述的关键调用栈中，结合源码，你可以找出一些关键信息：

1. Tomcat 等容器启动时，才会创建 FilterRegistrationBean；
2. FilterRegistrationBean 在被创建时（createBean）会创建 TimeCostFilter 来装配自身，TimeCostFilter 是通过 ResolveInnerBean 来创建的；
3. TimeCostFilter 实例最终是一种 InnerBean，我们可以通过下面的调试视图看到它的一些关键信息：

![image-20220812215418615](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202208122154800.png)

通过上述分析，可以看出最终 TimeCostFilter 实例是一种 InnerBean，所以自动注入不到也就非常合理了。

- 问题修正

```java
@Controller
@Slf4j
public class StudentController {
    @Autowired
    @Qualifier("com.spring.puzzle.filter.TimeCostFilter")
    FilterRegistrationBean timeCostFilter;
}
```

这里的关键点在于：

1. 注入的类型是 FilterRegistrationBean 类型，而不是 TimeCostFilter 类型；
2. 注入的名称是包含包名的长名称，即 com.spring.puzzle.filter.TimeCostFilter（不能用TimeCostFilter），以便于存在多个过滤器时进行精确匹配。

**案例 2：Filter 中不小心多次执行 doFilter()**

在上一个案例，我们主要都讨论了使用 @ServletComponentScan + @WebFilter 构建过滤器过程中的一些常见问题。

而在实际生产过程中，如果我们需要构建的过滤器是针对全局路径有效，且没有任何特殊需求（主要是指对 Servlet 3.0 的一些异步特性支持），那么完全可以直接使用 Filter 接口（或者继承 Spring 对 Filter 接口的包装类 OncePerRequestFilter），并使用 @Component 将其包装为 Spring 中的普通 Bean，也是可以达到预期的需求。

StudentController 保持功能不变，可以直接参考之前的代码。另外我们定义一个 DemoFilter 用来模拟问题，这个 Filter 标记了 @Component 且实现了 Filter 接口。

```java
@Component
public class DemoFilter implements Filter {
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) {
        try {
            //模拟异常
            System.out.println("Filter 处理中时发生异常");
            throw new RuntimeException();
        } catch (Exception e) {
            chain.doFilter(request, response);
        }
        chain.doFilter(request, response);
    }
}
```

全部代码实现完毕，执行后结果如下：

```
Filter 处理中时发生异常
......用户注册成功
......用户注册成功
```

这里我们可以看出，业务代码被执行了两次，这并不符合我们的预期。

- 案例解析

以 Tomcat 为例，我们先来看下它的 Filter 实现中最重要的类 ApplicationFilterChain。它采用的是责任链设计模式。责任链核心在于上下文 FilterChain 在不同对象 Filter 间的传递与状态的改变，通过这种链式串联，我们就可以对同一种对象资源实现不同业务场景的处理，达到业务解耦。整个 FilterChain 的结构就像这张图一样：

![image-20220816224711268](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202208162247544.png)

这里我们不妨还是带着两个问题去理解 FilterChain：

1. FilterChain 在何处被创建，又是在何处进行初始化调用，从而激活责任链开始链式调用？
2. FilterChain 为什么能够被链式调用，其内在的调用细节是什么？

我们直接查看负责请求处理的 StandardWrapperValve#invoke()，快速解决第一个问题：

```java
public final void invoke(Request request, Response response)
    throws IOException, ServletException {
    // 省略非关键代码
    // 创建filterChain
    ApplicationFilterChain filterChain =
        ApplicationFilterFactory.createFilterChain(request, wrapper, servlet);
    // 省略非关键代码
    try {
        if ((servlet != null) && (filterChain != null)) {
            // Swallow output if needed
            if (context.getSwallowOutput()) {
                // 省略非关键代码
                //执行filterChain
                filterChain.doFilter(request.getRequest(), response.getResponse());
                // 省略非关键代码
            }
            // 省略非关键代码
        }
    }
}
```

Spring 通过 ApplicationFilterFactory.createFilterChain() 创建 FilterChain，然后调用其 doFilter() 执行责任链。

接下来，我们来一起研究第二个问题，即 FilterChain 能够被链式调用的原因和内部细节。

首先查看 ApplicationFilterFactory.createFilterChain()，来看下 FilterChain 如何被创建，如下所示：

```java
public static ApplicationFilterChain createFilterChain(
    ServletRequest request, Wrapper wrapper, Servlet servlet) {
    // 省略非关键代码
    ApplicationFilterChain filterChain = null;
    if (request instanceof Request) {
        // 省略非关键代码
        // 创建Chain
        filterChain = new ApplicationFilterChain();
        // 省略非关键代码
    }
    // 省略非关键代码
    // Add the relevant path-mapped filters to this filter chain
    for (int i = 0; i < filterMaps.length; i++) {
        // 省略非关键代码
        ApplicationFilterConfig filterConfig = (ApplicationFilterConfig)
            context.findFilterConfig(filterMaps[i].getFilterName());
        if (filterConfig == null) {
            continue;
        }
        // 增加filterConfig到Chain
        filterChain.addFilter(filterConfig);
    }
    // 省略非关键代码
    return filterChain;
}
```

它创建 FilterChain，并将所有 Filter 逐一添加到 FilterChain 中。然后我们继续查看 ApplicationFilterChain 类及其 addFilter()：

```java
// 省略非关键代码
private ApplicationFilterConfig[] filters = new ApplicationFilterConfig[0];
private int pos = 0;
private int n = 0；
// 省略非关键代码
void addFilter(ApplicationFilterConfig filterConfig) {
    for(ApplicationFilterConfig filter:filters) {
        if(filter==filterConfig) {
            return;
        }
    }
    if (n == filters.length) {
        ApplicationFilterConfig[] newFilters = 
            new ApplicationFilterConfig[n + INCREMENT];
        System.arraycopy(filters, 0, newFilters, 0, n);
        filters = newFilters;
    }
    filters[n++] = filterConfig;
}
```

到这，Spring 就完成了 FilterChain 的创建准备工作。接下来，我们继续看 FilterChain 的执行细节，即 ApplicationFilterChain 的 doFilter()：

```java
public void doFilter(ServletRequest request, ServletResponse response)
    throws IOException, ServletException {
    if( Globals.IS_SECURITY_ENABLED ) {
        //省略非关键代码
        internalDoFilter(request,response);
        //省略非关键代码
    } else {
        internalDoFilter(request,response);
    }
}
```

这里逻辑被委派到了当前类的私有方法 internalDoFilter，具体实现如下：

```java
private void internalDoFilter(ServletRequest request, ServletResponse response) {
    if (pos < n) {
        // pos会递增
        ApplicationFilterConfig filterConfig = filters[pos++];
        try {
            Filter filter = filterConfig.getFilter();
            // 省略非关键代码
            // 执行filter
            filter.doFilter(request, response, this);
            // 省略非关键代码
        }
        // 省略非关键代码
        return;
    }
    // 执行真正实际业务
    servlet.service(request, response);
}
```

我们可以归纳下核心知识点：

1. ApplicationFilterChain 的 internalDoFilter() 是过滤器逻辑的核心；
2. ApplicationFilterChain 的成员变量 Filters 维护了所有用户定义的过滤器；
3. ApplicationFilterChain 的类成员变量 n 为过滤器总数，变量 pos 是运行过程中已经执行的过滤器个数；
4. filter.doFilter(request, response, this) 会调用过滤器实现的 doFilter()，注意第三个参数值为 this，即为当前 ApplicationFilterChain 实例 ，这意味着：用户需要在过滤器中显式调用一次 javax.servlet.FilterChain#doFilter，才能完成整个链路；
5. pos < n 意味着执行完所有的过滤器，才能通过 servlet.service(request, response) 去执行真正的业务。

从下面这张调用栈的截图中，可以看到，经历了一个很长的看似循环的调用栈，我们终于从internalDoFilter() 执行到了 Controller 层的 saveUser()。这个过程就不再一一细讲了。

![image-20220816223301964](https://technotes.oss-cn-shenzhen.aliyuncs.com/2022/202208162233201.png)

DemoFilter 代码中的 doFilter() 在捕获异常的部分执行了一次，随后在 try 外面又执行了一次，因而当抛出异常的时候，doFilter() 明显会被执行两次，相对应的
servlet.service(request, response) 方法以及对应的 Controller 处理方法也被执行了两次。

- 问题修正

只需要删掉重复的 filterChain.doFilter(request, response) 就可以了。

```java
@Component
public class DemoFilter implements Filter {
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) {
        try {
            //模拟异常
            System.out.println("Filter 处理中时发生异常");
            throw new RuntimeException();
        } catch (Exception e) {
            // chain.doFilter(request, response);
        }
        chain.doFilter(request, response);
    }
}
```

在使用过滤器的时候，一定要注意，不管怎么调用，不能多次调用 FilterChain#doFilter()。

# 14 | Spring Web 过滤器使用常见错误（下）

这节课我们来学习下容器启动时过滤器初始化以及排序注册等相关逻辑。

**案例 1：@WebFilter 过滤器使用 @Order 无效**

我们还是基于 Spring Boot 去开发学籍管理系统，启动程序的代码如下：

```java
@SpringBootApplication
@ServletComponentScan
@Slf4j
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
        log.info("启动成功");
    }
}
```

实现的 Controller 代码如下：

```java
@Controller
@Slf4j
public class StudentController {
    @PostMapping("/regStudent/{name)}")
    @ResponseBody
    public String saveUser(String name) throws Exception {
        System.out.println("......用户注册成功");
        return "success";
    }
}
```

现在，我们来实现两个新的过滤器，代码如下：

AuthFilter：例如，限制特定 IP 地址段（例如校园网内）的用户方可注册为新用户。

```java
@WebFilter
@Slf4j
@Order(2)
public class AuthFilter implements Filter {
    @SneakyThrows
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) {
        if(isPassAuth()) {
            System.out.println("通过授权");
            chain.doFilter(request, response);
        } else {
            System.out.println("未通过授权");
            ((HttpServletResponse)response).sendError(401);
        }
    }
    private boolean isPassAuth() throws InterruptedException {
        System.out.println("执行检查权限");
        Thread.sleep(1000);
        return true;
    }
}
```

TimeCostFilter：计算注册学生的执行耗时，需要包括授权过程。

```java
@WebFilter
@Slf4j
@Order(1)
public class TimeCostFilter implements Filter {
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) 
        throws IOException, ServletException {
        System.out.println("#开始计算接口耗时");
        long start = System.currentTimeMillis();
        chain.doFilter(request, response);
        long end = System.currentTimeMillis();
        long time = end - start;
        System.out.println("#执行时间(ms)：" + time);
    }
}
```

在上述代码中，我们使用了 @Order，期望 TimeCostFilter 先被执行，因为 TimeCostFilter 设计的初衷是统计这个接口的性能，所以是需要统计 AuthFilter 执行的授权过程的。

全部代码实现完毕，执行结果如下：

```
执行检查权限
通过授权
#开始计算接口耗时
......用户注册成功
#执行时间(ms)：33
```

从结果来看，执行时间并不包含授权过程，所以这并不符合我们的预期。

- 案例解析

```java
class WebFilterHandler extends ServletComponentHandler {
    WebFilterHandler() {
        super(WebFilter.class);
    }
    @Override
    public void doHandle(Map<String, Object> attributes, AnnotatedBeanDefinition beanDefinition,
                         BeanDefinitionRegistry registry) {
        BeanDefinitionBuilder builder = 
            BeanDefinitionBuilder.rootBeanDefinition(FilterRegistrationBean.class);
        builder.addPropertyValue("asyncSupported", attributes.get("asyncSupported"));
        builder.addPropertyValue("dispatcherTypes", extractDispatcherTypes(attributes));
        builder.addPropertyValue("filter", beanDefinition);
        builder.addPropertyValue("initParameters", extractInitParameters(attributes));
        String name = determineName(attributes, beanDefinition);
        builder.addPropertyValue("name", name);
        builder.addPropertyValue("servletNames", attributes.get("servletNames"));
        builder.addPropertyValue("urlPatterns", extractUrlPatterns(attributes));
        registry.registerBeanDefinition(name, builder.getBeanDefinition());
    }
    // 省略非关键代码
```

所有被 @WebFilter 注解的类，最终都会被包装为 FilterRegistrationBean 类的 BeanDefinition。虽然 FilterRegistrationBean 也拥有 Ordered 接口，但此处却并没有填充值，因为这里所有的属性都是从 @WebFilter 对应的属性获取的，而 @WebFilter 本身没有指定可以辅助排序的属性。

过滤器的执行顺序是由下面这个串联决定的：

```
RegistrationBean 中 order 属性的值 ->
ServletContextInitializerBeans 类成员变量 sortedList 中元素的顺序 ->
ServletWebServerApplicationContext 中 selfInitialize() 遍历
FilterRegistrationBean 的顺序 ->
addFilterMapBefore() 调用的顺序 ->
filterMaps 内元素的顺序 ->
过滤器的执行顺序
```

RegistrationBean 中 order 属性的值最终可以决定过滤器的执行顺序。但是可惜的是：当使用 @WebFilter 时，构建的 FilterRegistrationBean 并没有依据 @Order 的值去设置 order 属性，所以 @Order 失效了。

- 问题修正

实现自己的 FilterRegistrationBean 来配置添加过滤器，不再使用 @WebFilter。具体代码如下：

```java
@Configuration
public class FilterConfiguration {
    @Bean
    public FilterRegistrationBean authFilter() {
        FilterRegistrationBean registration = new FilterRegistrationBean();
        registration.setFilter(new AuthFilter());
        registration.addUrlPatterns("/*");
        registration.setOrder(2);
        return registration;
    }
    @Bean
    public FilterRegistrationBean timeCostFilter() {
        FilterRegistrationBean registration = new FilterRegistrationBean();
        registration.setFilter(new TimeCostFilter());
        registration.addUrlPatterns("/*");
        registration.setOrder(1);
        return registration;
    }
}
```












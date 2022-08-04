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
























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




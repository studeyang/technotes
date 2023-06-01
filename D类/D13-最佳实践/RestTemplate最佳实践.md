# 用法一：POST 请求

```java
public <R, B> R postForObject(String url, B body, Class<R> responseType) {
    HttpHeaders headers = new HttpHeaders();
    headers.setContentType(MediaType.APPLICATION_JSON);
    HttpEntity<B> request = new HttpEntity<>(body, headers);
    return restTemplate.postForObject(url, request, responseType);
}
```

```java
public BaseResponse example(ApplySignRequest request) {
    String json = JSON.toJSONString(request);
    return restTemplateWrapper.postForObject(baseUrl + "/example", json, BaseResponse.class);
}
```

# 用法二：PUT 请求

```java
public <R, B> R putForObject(String url, B body, Class<R> responseType) {
    HttpHeaders headers = new HttpHeaders();
    headers.setContentType(MediaType.APPLICATION_JSON);
    HttpEntity<B> request = new HttpEntity<>(body, headers);
    ResponseEntity<R> responseEntity = restTemplate.exchange(url, HttpMethod.PUT, request, responseType);
    if (!responseEntity.getStatusCode().is2xxSuccessful()) {
        throw new RestException(FAIL_MESSAGE, url, responseEntity.getStatusCode());
    }
    return responseEntity.getBody();
}
```

```java
public BaseResponse update(UpdateSignRequest request) {
    String json = JSON.toJSONString(request);
    return restTemplateWrapper.putForObject(baseUrl + "/sms/sign", json, BaseResponse.class);
}
```

# 用法三：返回 List\<T\>

```java
public <T, R, B> List<R> exchangeForList(String url,  HttpMethod httpMethod,  HttpHeaders headers,  B body,
                                         Class<T> arrayType, Object... uriVariables) {
    HttpEntity<B> httpEntity = new HttpEntity<>(body, headers);
    ResponseEntity<T> responseEntity = restTemplate.exchange(url, httpMethod, httpEntity, arrayType, uriVariables);
    if (!responseEntity.getStatusCode().is2xxSuccessful()) {
        throw new RestException(FAIL_MESSAGE, url, responseEntity.getStatusCode());
    }
    // User[]
    R[] r = (R[]) responseEntity.getBody();
    return Arrays.stream(r)
            .collect(Collectors.toList());
}
```

```java
public List<User> example() {
    return restTemplateWrapper.exchangeForList(baseUrl + "/user", HttpMethod.GET, new HttpHeaders(), null, User[].class);
}
```


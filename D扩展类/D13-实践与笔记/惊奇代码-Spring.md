## 一、Spring 事务

初始化事务管理器。

```java
package org.springframework.boot.autoconfigure.jdbc;

@Configuration
@ConditionalOnClass({ JdbcTemplate.class, PlatformTransactionManager.class })
@AutoConfigureOrder(Ordered.LOWEST_PRECEDENCE)
public class DataSourceTransactionManagerAutoConfiguration {

	@Configuration
	@ConditionalOnSingleCandidate(DataSource.class)
	static class DataSourceTransactionManagerConfiguration {
		private final DataSource dataSource;
		DataSourceTransactionManagerConfiguration(DataSource dataSource) {
			this.dataSource = dataSource;
		}

		@Bean
		@ConditionalOnMissingBean(PlatformTransactionManager.class)
		public DataSourceTransactionManager transactionManager() {
			return new DataSourceTransactionManager(this.dataSource);
		}
	}
}
```

使用事务。

```java
@Autowired
private PlatformTransactionManager transactionManager;

public void generateBill2024Version(List<String> companyIds, LocalDateTime executeTime) {
    TransactionStatus status = transactionManager.getTransaction(new DefaultTransactionDefinition());
        try {
            if (CollectionUtils.isNotEmpty(toUpdates)) {
                billToGenerateBizService.updateBatchById(toUpdates);
            }
            // 4. 生成账单
            afterGenerate(bills);
            transactionManager.commit(status);
        } catch (Exception e) {
            log.error("生成技术服务费账单失败: {}", e.getMessage(), e);
            transactionManager.rollback(status);
    }
}
```

## 二、RestTemplate

### 用法一：POST 请求

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

### 用法二：PUT 请求

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

### 用法三：返回 List\<T\>

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

## 三、有条件地加载Bean

```java
@ConditionalOnClass({HikariDataSource.class})
@ConditionalOnMissingBean({DataSource.class})
@ConditionalOnProperty(
    name = {"spring.datasource.type"},
    havingValue = "com.zaxxer.hikari.HikariDataSource",
    matchIfMissing = true
)
static class HiKari {
    Hikari() {
    }
}
```

## 四、MockHttpServletRequest

供单元测试使用的 HttpServletRequest 实现。

```java
package com.fcbox.send.operation.controller.op.comment;

import junit.framework.TestCase;
import org.junit.Before;
import org.junit.runner.RunWith;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.test.context.junit4.SpringRunner;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

@RunWith(SpringRunner.class)
@SpringBootTest(classes = SendOperationApplication.class)
public class FcboxSendCommentControllerTest extends TestCase {

    @Before
    public void setUp() {
        MockHttpServletRequest servletRequest = new MockHttpServletRequest();
        servletRequest.addParameter("userId", "test");
        servletRequest.addParameter("innerUserName", "test");

        ServletRequestAttributes requestAttributes = new ServletRequestAttributes(servletRequest);
        RequestContextHolder.setRequestAttributes(requestAttributes);
    }
}
```

## 五、PropertyOrderConfig

自定义配置顺序。

```java
package io.github.studeyang.commons;

import org.springframework.context.EnvironmentAware;
import org.springframework.core.env.CompositePropertySource;
import org.springframework.core.env.ConfigurableEnvironment;
import org.springframework.core.env.Environment;
import org.springframework.core.env.PropertySource;
import org.springframework.stereotype.Component;

@Component
public class PropertyOrderConfig implements EnvironmentAware {

    @Override
    public void setEnvironment(Environment environment) {
        ConfigurableEnvironment configurableEnvironment = (ConfigurableEnvironment) environment;

        CompositePropertySource composite = new CompositePropertySource("PropertyOrderConfig");
        composite.addPropertySource(getPropertySource(configurableEnvironment));

        configurableEnvironment.getPropertySources().addFirst(composite);
    }

    private PropertySource<?> getPropertySource(ConfigurableEnvironment environment) {
        // 要提前的配置名
        return environment.getPropertySources().get("Inlined Test Properties");
    }

}
```


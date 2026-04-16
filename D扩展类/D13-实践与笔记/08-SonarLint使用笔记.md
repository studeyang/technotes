## 一、忽略代码扫描

### 1.1 标准SonarQube注释方式

#### 忽略单个规则

```java
@SuppressWarnings("java:S1234") // 忽略特定规则
public void methodWithIssue() {
    // 有问题的代码
}
```

#### 忽略多个规则

```java
@SuppressWarnings({"java:S1234", "java:S5678"}) // 忽略多个规则
public void methodWithMultipleIssues() {
    // 有问题的代码
}
```

#### 忽略文件中的所有问题

```java
@SuppressWarnings("all") // 忽略整个文件中的所有问题
public class ClassWithIssues {
    // 类内容
}
```

### 1.2 SonarLint专用注释

#### 针对代码块

```java
// sonarignore:start
public void problematicMethod() {
    // 这段代码将被SonarLint忽略
}
// sonarignore:end
```

#### 针对特定规则

```java
// sonarignore:ruleKey S1234
public void methodWithSpecificIssue() {
    // 仅忽略S1234规则的代码
}
```

### 1.3 行内忽略

```java
public void someMethod() {
    String password = "123456"; // NOSONAR - 忽略这一行的所有问题
    int unusedVar = 42; // sonarignore:ruleKey S1481 - 仅忽略未使用变量警告
}
```




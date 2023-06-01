# 添加自定义变量

请求体

```json
{
	"messageId": "{{messageId}}",
	"topic": "alpha-example",
	"type": "com.casstime.ec.cloud.example.event.ExampleEvent",
	"service": "postman",
	"content": "{\"jsonMessageType\":\"com.casstime.ec.cloud.example.event.ExampleEvent\",\"id\":\"{{messageId}}\",\"usage\":\"EVENT\",\"service\":\"postman\",\"topic\":\"alpha-example\",\"timeStamp\":{{$timestamp}},\"content\":\"1733\",\"handleCost\":100,\"exception\":false,\"now\":{{$timestamp}}}",
	"createdAt": "{{$timestamp}}",
	"usage": "EVENT",
	"cluster": "cassmall",
	"env": "default"
}
```

`messageId`变量定义

```javascript
// 在 Pre-request Script 增加以下代码
function randomstr(length, chars) {
  var result = '';
  for (var i =length; i > 0; i--) {
    result += chars[Math.floor(Math.random() * chars.length)];
  }
  return result;
}
var random = randomstr(20, '0123456789abcdef');
pm.environment.set("messageId", "TEST" + random);
```


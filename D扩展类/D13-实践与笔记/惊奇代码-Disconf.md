## 一、Disconf

手动注入配置值。

```java
package com.fcbox.send.order.encrypt;

import com.baidu.disconf.client.store.DisconfStoreProcessor;
import com.baidu.disconf.client.store.DisconfStoreProcessorFactory;
import com.baidu.disconf.client.store.processor.model.DisconfValue;

import java.util.HashMap;
import java.util.Map;

public class DisconfMock {

    private static final DisconfStoreProcessor disconfStoreProcessor = DisconfStoreProcessorFactory.getDisconfStoreFileProcessor();

    public static void mockConfig(Integer value) {
        Map<String, Object> fileData = new HashMap<>();
        fileData.put("write.encrypt.switch", String.valueOf(value));
        disconfStoreProcessor.inject2Store("encrypt.properties", new DisconfValue(null, fileData));
    }
}
```


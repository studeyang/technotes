RSA 是一种非对称的签名算法，即签名密钥（私钥）与验签密钥（公钥）是不一样的，私钥用于签名，公钥用于验签。 其原理如下：

![](https://technotes.oss-cn-shenzhen.aliyuncs.com/2023/image-20230511140521053.png)

> 上图译自[RSA Data Security Digital Signature Process](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-2000-server/cc962021(v%3dtechnet.10)#rsa-data-security-digital-signature-process)

排列组合是指的生成签名原串的过程。

**校验规则**： 当接收方的期待串与签名原串一致时， 校验成功；否则校验失败。
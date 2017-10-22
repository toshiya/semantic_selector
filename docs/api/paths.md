
<a name="paths"></a>
## Paths

<a name="inference-input_tags"></a>
### inference api for input tags
```
POST /inference
```


#### Description
return an infered label of the given input tag.


#### Parameters

|Type|Name|Schema|
|---|---|---|
|**Body**|**html**  <br>*required*|[html](#html)|


#### Responses

|HTTP Code|Description|Schema|
|---|---|---|
|**200**|正常に推定処理が完了しました|[inference](#inference)|
|**400**|リクエストデータが不正です|No Content|
|**500**|API 側の問題による失敗です|No Content|


#### Consumes

* `application/json`


#### Produces

* `application/json`




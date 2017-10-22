
<a name="paths"></a>
## Paths

<a name="inference-input_tags"></a>
### inference api for input tags
```
POST /inference
```


#### Description
return an infered topic of the given input tag.


#### Parameters

|Type|Name|Schema|
|---|---|---|
|**Body**|**html**  <br>*required*|[html](#html)|


#### Responses

|HTTP Code|Description|Schema|
|---|---|---|
|**200**|successfull inference|[inference](#inference)|
|**400**|invalid request data|No Content|
|**500**|internal server error|No Content|


#### Consumes

* `application/json`


#### Produces

* `application/json`




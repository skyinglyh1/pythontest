<h1 align="center">Python Test</h1>

## Usage

#### 部署合约到区块链
python demo.py -m "./deploy.json"

deploy.json配置文件如下：
```
{
  "rpc_address": "http://127.0.0.1:20336", // 节点IP
  "code": "",                              //合约code字节码
  "need_storage": "true",                  //是否需要存储
  "name": "record",                        //合约名
  "code_version": "1",                     //合约版本
  "author": "sss",                         //合约作者
  "email": "sss",                          //作者email
  "desp": "record contract",               //合约描述信息
  "payer_address": "AazEvfQPcQ2GEFFPLF1ZLwQ7K5jDn81hve",//交易费用付款账户
  "payer_password":"111111",             //账户密码
  "wallet_file_path":"./test.json",      //钱包文件
  "gas_limit": 20200000,
  "gas_price": 0,
  "save_file":"./deploy.csv"             //测试结果保存的文件
}
```


#### 调用合约中的方法
python demo.py -i "./invoke_param/invoke.json"



## Site

* https://ont.io/

## License

The Ontology library (i.e. all code outside of the cmd directory) is licensed under the GNU Lesser General Public License v3.0, also included in our repository in the License file.

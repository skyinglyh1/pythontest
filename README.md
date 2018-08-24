<h1 align="center">Python Test</h1>

## Usage

#### Deploy smart contract to blockchain

```
python demo.py -m ./deploy.json
```


Configuration of deploy.json file：
```
{
  "rpc_address": "http://127.0.0.1:20336",      // Node IP
  "code": "./contract/Token/Token.avm",         //Path of .avm code file
  "need_storage": "true",                       //Need storage or not
  "name": "OntTestToken",                       //Contract name
  "code_version": "codeVersion1",               //Contract version
  "author": "authorTest",                       //Contract author
  "email": "emailTest",                         //Author email
  "desp": "contractDescription",                //Contract Description
  "payer_address": "AQf4Mzu1YJrhz9f3aRkkwSm9n3qhXGSh4p",    //Account to pay for deploying
  "payer_password":"***",                    // account password
  "wallet_file_path":"./deploy_wallet.json",    //Path of wallet file
  "gas_limit": 20600000,
  "gas_price": 0,
  "save_file":"./contract/Token/deploy.csv"     //Path of file for saving migrating test results
}
```


#### The way to invoke methods in contract
Once your invoke.json file has been correctly configured, you can test the methods in your contract, whether one by one or once for all.

###### Test the methods one by one
To check the name of the contract:<br/>

```
python demo.py -i ./contract/Token/invoke.json -f name
or
python demo.py -i ./contract/Token/invoke.json -f name1,name2
```

<br/> "demo.py" means the testing script for smart contract.
<br/> "-i" means invoking the methods in smart contract.
<br/> "./contract/Token/invoke.json" is the path of configuration file for the methods within your smart contract.
<br/> "-f" means you're invoking the desginated function
<br/> "name" means the name of function that you are invoking.

example:

To transfer some token: <br/>

```
python demo.py -i ./contract/Token/invoke.json -f transfer
```

###### Test the methods once for all
After you type the following command, all the methods/functions will be tested and run based on your configuration in "./contract/Token/invoke.json" file.<br/>

```
python demo.py -i "./contract/Token/invoke.json"
```




Configuration of invoke.json file：
```
{
  "rpc_address": "http://127.0.0.1:20336",      //Node IP
  "payer_address": "AQf4Mzu1YJrhz9f3aRkkwSm9n3qhXGSh4p",       //Account to pay for invoking
  "payer_password": "***",                      //account password
  "wallet_file_path": "./invoke_wallet.json",   //Path of wallet file
  "gas_limit": 20000,
  "gas_price": 0,
  "abi_path": "./contract/Token/TokenAbi.json", //Path of abi.json file
  "save_file": "./contract/Token/invoke.csv",   //Path of file for saving invoking test results
  "function": {
    "name": {                                   //Function name
      "function_name": "name",                  //Function name
      "function_param": {                       //Function parameters
      },
      "pre_exec": true                          //Need to pre-execute or not
    },
    "transfer": {                                           
      "function_name": "transfer",                         
      "function_param": {
        "fromAddr": "ASUwFccvYFrrWR6vsZhhNszLFNvCLA5qS6",   
        "toAddr": "AQf4Mzu1YJrhz9f3aRkkwSm9n3qhXGSh4p",
        "value": 1000000000000000
      },
      "signers":{                               //For the use fo signature
        "m": 1,                                 //Single signature
        "signer":{                              //Signature account
          "walletpath": "invoke_wallet.json",   //Sig account wallet path
          "address": "ASUwFccvYFrrWR6vsZhhNszLFNvCLA5qS6", // Sig account address
          "password": "***"                     // Sig account password
        }
      },
      "pre_exec": false                         //Need pre-execute or not
    }
  }
}
```


## Site

* https://ont.io/

## License

The Ontology library (i.e. all code outside of the cmd directory) is licensed under the GNU Lesser General Public License v3.0, also included in our repository in the License file.

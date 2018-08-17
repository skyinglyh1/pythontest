import csv
import json
import os
import sys, getopt
import time
from collections import namedtuple
from ontology.common.address import Address
from ontology.ont_sdk import OntologySdk
from ontology.smart_contract.neo_contract.abi.abi_info import AbiInfo


def main(argv):
   try:
      opts, args = getopt.getopt(argv, "hm:i:", ["migrate=", "invoke="])
   except getopt.GetoptError:
      print('test.py [-m|--migrate] [-i|--invoke] ')
      sys.exit(2)
   m = {}
   for opt, arg in opts:
      if opt == '-h':
         print('test.py [-m|--migrate] [-i|--invoke] ')
         sys.exit()
      elif opt in ("-m", "--migrate"):
         m["func"] = "migrate"
         if "json" in str(arg):
             with open(arg, "r") as f:
                 r = json.load(f, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
                 m["rpc_address"] = r.rpc_address
                 m["need_storage"] = r.need_storage
                 m["name"] = r.name
                 m["code_version"] = r.code_version
                 m["author"] = r.author
                 m["email"] = r.email
                 m["desp"] = r.desp
                 m["payer_address"] = r.payer_address
                 m["payer_password"] = r.payer_password
                 m["wallet_file_path"] = r.wallet_file_path
                 m["gas_limit"] = r.gas_limit
                 m["gas_price"] = r.gas_price
                 m["save_file"] = r.save_file
                 if ".avm" in r.code:
                     with open(r.code, "r") as f2:
                         m["code"] = f2.read()
                 else:
                     m["code"] = r.code
                 m["contract_address"] = Address.address_from_vm_code(m["code"]).to_hex_str()
         else:
             temp = str(arg).split(",")
             for i in temp:
                 t = str(i).split("=")
                 m[t[0]] = t[1]
      elif opt in ("-i", "--invoke"):
         m["func"] = "invoke"
         if "json" in str(arg):
             with open(arg, "r") as f:
                 r = json.load(f, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
                 m["rpc_address"] = r.rpc_address
                 m["acct_address"] = r.acct_address
                 m["acct_password"] = r.acct_password
                 m["payer_address"] = r.payer_address
                 m["payer_password"] = r.payer_password
                 m["wallet_file_path"] = r.wallet_file_path
                 m["gas_limit"] = r.gas_limit
                 m["gas_price"] = r.gas_price
                 m["abi_path"] = r.abi_path
                 m["save_file"] = r.save_file
                 m["function"] = r.function
         else:
             temp = str(arg).split(",")
             for i in temp:
                 t = str(i).split("=")
                 m[t[0]] = t[1]
      else:
         print('test.py [-m|--migrate] [-i|--invoke] ')
         sys.exit()

   sdk = OntologySdk()
   sdk.set_rpc(m["rpc_address"])
   if m["func"] is "migrate":
       need_storage = False
       if m["need_storage"] is 'true':
           need_storage = True
       tx = sdk.neo_vm().make_deploy_transaction(m["code"], need_storage, m["name"], m["code_version"], m["author"]
                                            , m["email"], m["desp"], m["payer_address"], m["gas_limit"], m["gas_price"])
       sdk.wallet_manager.open_wallet(m["wallet_file_path"])
       acct = sdk.wallet_manager.get_account(m["payer_address"], m["payer_password"])
       sdk.sign_transaction(tx, acct)
       sdk.set_rpc(m["rpc_address"])
       try:
           print("deploying，please waiting ...")
           res = sdk.rpc.send_raw_transaction(tx)
           print("txhash:", res)
           for i in range(10):
               time.sleep(1)
               res = sdk.rpc.get_smart_contract(m["contract_address"])
               if res == "":
                   continue
               else:
                   print("deploy success")
                   break
           save_file(m, "success")
       except Exception as e:
           print(e)
           save_file(m, e)
   elif m["func"] is "invoke":
       func_map = {}
       t = 0
       for i in list(m["function"]):
           func_list = []
           func_list.append(i.function_name)
           func_list.append(i.pre_exec)
           for j in list(i.function_param):
               func_list.append(j)
           func_map["function" + str(t)] = func_list
           t = t + 1
       with open(str(m["abi_path"]), "r") as f:
           abi = json.loads(f.read(), object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
           abi_info = AbiInfo(abi.hash, abi.entrypoint, abi.functions, abi.events)
           contract_address = bytearray.fromhex(str(abi.hash)[2:])
           m["contract_address"] = contract_address.hex()
           contract_address.reverse()
           sdk.wallet_manager.open_wallet(m["wallet_file_path"])
           acct = sdk.wallet_manager.get_account(m["acct_address"], m["acct_password"])
           payer = sdk.wallet_manager.get_account(m["payer_address"], m["payer_password"])
           func_l = []
           for func_info in func_map.values():
               func = abi_info.get_function(func_info[0])
               params = []
               l = []
               l.append(func_info[0])
               l.append(func_info[1])
               temp_l = ""
               for i in range(len(func_info)):
                   if i == 0 or i == 1:
                       continue
                   temp_l += func_info[i] + ":"
                   if func.parameters[i-2].type == "String":
                       params.append(str(func_info[i]))
                   if func.parameters[i-2].type == "ByteArray":
                       params.append(bytearray(func_info[i].encode()))
                   if func.parameters[i-2].type == "Integer":
                       params.append(func_info[i])
               l.append(temp_l[:len(temp_l)-1])
               if len(params) == 1:
                   func.set_params_value(params[0])
               elif len(params) == 2:
                   func.set_params_value(params[0], params[1])
               elif len(params) == 3:
                   func.set_params_value(params[0], params[1], params[2])
               elif len(params) == 4:
                   func.set_params_value(params[0], params[1], params[2], params[3])
               elif len(params) == 5:
                   func.set_params_value(params[0], params[1], params[2], params[3], params[4])
               elif len(params) == 6:
                   func.set_params_value(params[0], params[1], params[2], params[3], params[4], params[5])
               elif len(params) == 7:
                   func.set_params_value(params[0], params[1], params[2], params[3], params[4], params[5], params[6])
               pre_exec = False
               if func_info[1] == "true":
                   pre_exec = True
               try:
                   print("")
                   print("invoking, please waiting ...")
                   print("method: " + func_info[0])
                   res = sdk.neo_vm().send_transaction(contract_address, acct, payer, m["gas_limit"], m["gas_price"], func, pre_exec)
                   if not pre_exec:
                       time.sleep(6)
                       print("txhash:", res)
                       print("Event:", sdk.rpc.get_smart_contract_event_by_tx_hash(res))
                       l.append(res)
                   else:
                       print(res)
                       print("res:", (bytearray.fromhex(res)).decode('utf-8'))
                       l.append((bytearray.fromhex(res)).decode('utf-8'))
               except Exception as e:
                   print("Error:", e)
                   l.append(e)
               func_l.append(l)
           save_file(m, "", func_l)
   else:
       print("only support migrate and invoke")


def save_file(m: [], res: str, func_l = None):
    ishasheader = False
    if os.path.exists(m["save_file"]):
        ishasheader = True
    if m["func"] == "migrate":
        with open(m["save_file"], "a") as csvfile:
            writer = csv.writer(csvfile)
            if not ishasheader:
                writer.writerow(
                    ["need_storage", "name", "code_version", "author", "email", "desp", "payer_address", "gas_limit",
                     "gas_price"])
            writer.writerow([m["need_storage"], m["name"], m["code_version"], m["author"], m["email"], m["desp"],
                             m["payer_address"], m["gas_limit"], m["gas_price"], res])
    elif m["func"] == "invoke":
        with open(m["save_file"], "a") as csvfile:
            writer = csv.writer(csvfile)
            if not ishasheader:
                writer.writerow(["contract_address", "acct_address", "payer_address", "gas_limit", "gas_price","function_name","pre_exec","params", "result"])
            for i in func_l:
                writer.writerow([m["contract_address"], m["acct_address"], m["payer_address"], m["gas_limit"], m["gas_price"], i[0],i[1], i[2], i[3]])


if __name__ == "__main__":
   main(sys.argv[1:])
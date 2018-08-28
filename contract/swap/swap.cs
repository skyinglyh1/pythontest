using Ont.SmartContract.Framework;
using Ont.SmartContract.Framework.Services.Ont;
using Ont.SmartContract.Framework.Services.System;
using System;
using System.ComponentModel;
using System.Numerics;

namespace SwapContract
{
    public class SwapContract : SmartContract
    {
        // 合约管理员
        //public static readonly byte[] admin = "AT4dGijAQSMcN5mj2q7ePTWcKFEnG1qeu3".ToScriptHash();
        public static readonly byte[] admin = {123,212,116,117,198,162,213,5,136,227,129,61,35,74,2,183,243,175,138,83};


        // 有叻积分合约
        [Appcall("749a701ae89c0dbdab9b4b660ba84ee478004219")]
        public static extern object YL(string method, object[] parameter);

        // 全家积分合约
        [Appcall("ca839e7fcb4a892767b4138f23d7a5b5298ea2c7")]
        public static extern object QJ(string method, object[] parameter);

        // 全家base账户
        //public static readonly byte[] QjBaseAcc = "ARR5ywDEx3ybXkMGmZPFYu9hiC8J4xvNdc".ToScriptHash();
        public static readonly byte[] QjBaseAcc = {105,194,209,201,159,3,89,243,123,222,255,101,226,183,187,140,60,101,45,211};
        // 全家recycle账户
        //public static readonly byte[] QjRecAcc = "AacHGsQVbTtbvSWkqZfvdKePLS6K659dgp".ToScriptHash();
        public static readonly byte[] QjRecAcc = {206,153,244,3,154,222,42,132,236,222,27,208,220,233,217,195,155,63,160,133};
        // 有叻base账户
        //public static readonly byte[] YlBaseAcc = "ASUwFccvYFrrWR6vsZhhNszLFNvCLA5qS6".ToScriptHash();
        public static readonly byte[] YlBaseAcc = {117,117,82,107,192,102,163,172,198,171,177,52,17,156,214,212,169,4,25,105};
        // 有叻recycle账户
        //public static readonly byte[] YlRecAcc = "AWf8NiLzXSDf1JB2Ae6YUKSHke4yLHMVCm".ToScriptHash();
        public static readonly byte[] YlRecAcc = {248,142,51,220,214,177,110,235,27,218,59,86,23,47,140,20,114,119,159,152};


        public static Object Main(string operation, params object[] args)
        {
            // 全家兑换有叻
            if (operation == "YLSwap")
            {
                if (args.Length != 2) return false;
                byte[] acc = (byte[])args[0];
                ulong value = (ulong)args[1];
                YLSwap(acc, value);
            }

            // 有叻兑换全家
            if (operation == "QJSwap")
            {
                if (args.Length != 2) return false;
                byte[] acc = (byte[])args[0];
                ulong value = (ulong)args[1];
                QJSwap(acc, value);
            }

            // 设置有叻兑换全家比率
            if (operation == "SetFeeRate")
            {
                if (args.Length != 1) return false;
                ulong percentage = (ulong)args[0];
                SetFeeRate(percentage);
            }

            // 设置手续费比率
            if (operation == "SetSwapRate")
            {
                if (args.Length != 2) return false;
                BigInteger YlBase = (BigInteger)args[0];
                BigInteger Qjrate = (BigInteger)args[1];
                SetSwapRate(YlBase, Qjrate);
            }

            // 获取当前手续费比率（百分比）
            if (operation == "GetFeeRate")
            {
                return GetFeeRate();
            }

            // 获取永乐兑换全家积分，永乐的base基准
            if (operation == "GetYlSwapBase")
            {
                return GetYlSwapBase();
            }

            // 获取全家兑换永乐积分，全家的base基准
            if (operation == "GetQjSwapBase")
            {
                return GetQjSwapBase();
            }

            return false;
        }

        public static bool YLSwap(byte[] acc, ulong value)
        {
            //if (!Runtime.CheckWitness(acc))
            //{
            //    return false;
            //}
            if (value < 0)
            {
                return false;
            }

            StorageContext context = Storage.CurrentContext;
            ulong YlBase = (ulong)Storage.Get(context, "YlBaseRate").AsBigInteger();
            ulong QjBase = (ulong)Storage.Get(context, "QjBaseRate").AsBigInteger();
            ulong feeRate = (ulong)Storage.Get(context, "feeRate").AsBigInteger();

            if (YlBase < 0 || QjBase < 0 || feeRate < 0)
            {
                return false;
            }

            ulong YlValue = (value * YlBase / QjBase) * (100 - feeRate) / 100;

            //将全家用户的积分转移到有叻的回收账户
            object[] args = new object[] { acc, YlRecAcc, value };

            bool b = (bool)QJ("transfer", args);
            if (!b)
            {
                return false;
            }

            //将有叻合约的base账户的积分转移到全家用户的账户
            args = new object[] { YlBaseAcc, acc, YlValue };

            b = (bool)YL("transfer", args);
            if (!b)
            {
                return false;
            }

            return true;
        }

        public static bool QJSwap(byte[] acc, ulong value)
        {
            //if (!Runtime.CheckWitness(acc))
            //{
            //    return false;
            //}
            if (value < 0)
            {
                return false;
            }

            StorageContext context = Storage.CurrentContext;
            ulong YlBase = (ulong)Storage.Get(context, "YlBaseRate").AsBigInteger();
            ulong QjBase = (ulong)Storage.Get(context, "QjBaseRate").AsBigInteger();
            ulong feeRate = (ulong)Storage.Get(context, "feeRate").AsBigInteger();


            if (YlBase < 0 || QjBase < 0 || feeRate < 0)
            {
                return false;
            }

            ulong QjValue = (value * QjBase / YlBase) * (100 - feeRate) / 100;

            //将有叻用户的积分转移到全家的回收账户
            object[] args = new object[] { acc, YlBaseAcc, value };

            bool b = (bool)YL("transfer", args);
            if (!b)
            {
                return false;
            }

            //将全家合约的base账户的积分转移到有叻用户的账户
            args = new object[] { QjBaseAcc, acc, QjValue };

            b = (bool)QJ("transfer", args);
            if (!b)
            {
                return false;
            }

            return true;
        }

        public static bool SetFeeRate(ulong percentage)
        {
            if (percentage < 0 || percentage >= 100)
            {
                return false;
            }

            //if (!Runtime.CheckWitness(admin))
            //{
            //    return false;
            //}

            StorageContext context = Storage.CurrentContext;
            Storage.Put(context, "feeRate", percentage);
            return true;
        }

        public static bool SetSwapRate(BigInteger YlBase, BigInteger QjBase)
        {
            if (YlBase <= 0 || QjBase <= 0)
            {
                return false;
            }
            1111
            //if (!Runtime.CheckWitness(admin))
            //{
            //    return false;
            //}

            StorageContext context = Storage.CurrentContext;
            Storage.Put(context, "YlBaseRate", YlBase);
            Storage.Put(context, "QjBaseRate", QjBase);
            return true;
        }

        public static BigInteger GetFeeRate()
        {
            Runtime.Notify(Storage.Get(Storage.CurrentContext, "feeRate"));
            return Storage.Get(Storage.CurrentContext, "feeRate").AsBigInteger();
        }

        public static BigInteger GetYlSwapBase()
        {
            Runtime.Notify(Storage.Get(Storage.CurrentContext, "YlBaseRate"));
            return Storage.Get(Storage.CurrentContext, "YlBaseRate").AsBigInteger();
        }

        public static BigInteger GetQjSwapBase()
        {
            Runtime.Notify(Storage.Get(Storage.CurrentContext, "QjBaseRate"));
            return Storage.Get(Storage.CurrentContext, "QjBaseRate").AsBigInteger();
        }
    }
}
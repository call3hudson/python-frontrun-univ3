import re
from constant import usdt, dai, fee_tier

def take_fn_name(fnCode): 
    return re.findall("Function (.*)\(.*\)", fnCode)[0]

def get_pool(tokenA, tokenB, fee):
    return


def validate_token_path(path):
    # For now, we only perform frontrunning on USDT-DAI pair
    
    (token0, tier, token1) = path

    print(token0)
    print(token1)
    print(tier)

    if (token0.__str__() != usdt):
        return False
    
    if (token1.__str__() != dai):
        return False
    
    if (tier.__str__() != fee_tier):
        return False

    return True

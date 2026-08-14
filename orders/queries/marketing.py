
from .delivery import get_delivery_totals
from .transactions import get_transaction_totals

def get_marketing_summary(order):
    delivery = get_delivery_totals(order)
    transaction = get_transaction_totals(order)

    return {
        "total_SO": transaction["by_type"]["SO"]["qty"],
        "total_SAM": transaction["by_type"]["SAM"]["qty"],
        "total_CRET": transaction["by_type"]["CRET"]["qty"],
        "total_CBO": transaction["by_type"]["CBO"]["qty"],

        "total_MLOAD": delivery["by_type"]["MLOAD"]["qty"],
        "total_MRET": delivery["by_type"]["MRET"]["qty"],
        "total_VBO": delivery["by_type"]["VBO"]["qty"],
    }

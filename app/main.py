from app.calc.constants import CONSTANTS
from app.calc.json_calculator import calculate_field

print(
    calculate_field(
        "본인부담금",
        {
            "등급체계구분": "인정조사",
            "월한도액": CONSTANTS["월한도액_인정조사"][1],
            "소득등급": "가",
        },
    )
)
print()

print("산정특례 / 2등급 / 취약가구 / 힉교생활O / 직장생활X / 확장형 / 다형")
monthly_limit_basic = calculate_field(
    "월한도액_산정특례",
    {
        "기본급여": CONSTANTS["월한도액_인정조사"][2],
        "추가특성": "2등급이하취약가구",
        "학교생활여부": True,
        "직장생활여부": False,
    },
)
monthly_limit_extended = calculate_field(
    "월한도액_확장형", {"월한도액_기본형": monthly_limit_basic}
)
print(
    calculate_field(
        "본인부담금_확장형",
        {
            "등급체계구분": "산정특례",
            "월한도액": monthly_limit_extended,
            "소득등급": "다",
        },
    )
)
print()

print(calculate_field("활동보조30분심야단가"))
print()

print(
    calculate_field(
        "방문목욕40분",
        {"방문목욕기본단가": CONSTANTS["방문목욕기본단가"]["가정내입욕"]},
    )
)
print()

print(
    calculate_field(
        "방문목욕40분",
        {"방문목욕기본단가": CONSTANTS["방문목욕기본단가"]["차량내입욕"]},
    )
)

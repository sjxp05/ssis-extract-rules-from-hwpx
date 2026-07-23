from app.calc.constants import CONSTANTS
from app.calc.json_calculator import calculate_field

# ================================================================================
# 인정조사 월한도액 확장형만 미리 계산해서 재활용
monthly_limits = {}
for k, v in CONSTANTS["월한도액_인정조사"].items():
    monthly_limits[k] = calculate_field(
        "월한도액_인정조사_확장형", {"월한도액_기본형": v}
    )
CONSTANTS["월한도액_인정조사_확장형"] = monthly_limits
print()
# ================================================================================


print("인정조사 / 1등급 / 가형")
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


print("인정조사 / 4등급 / 라형")
print(
    calculate_field(
        "본인부담금",
        {
            "등급체계구분": "인정조사",
            "월한도액": CONSTANTS["월한도액_인정조사"][4],
            "소득등급": "라",
        },
    )
)
print()


print("인정조사 / 1등급 / 확장형 / 바형")
print(
    calculate_field(
        "본인부담금_확장형",
        {
            "등급체계구분": "인정조사",
            "월한도액": CONSTANTS["월한도액_인정조사_확장형"][1],
            "소득등급": "바",
        },
    )
)
print()


print("산정특례 / 2등급 / 보호자일시부재 / 학교생활O / 직장생활O / 마형")
monthly_limit = calculate_field(
    "월한도액_산정특례",
    {
        "기본급여등급": 2,
        "추가특성": "보호자일시부재",
        "학교생활여부": True,
        "직장생활여부": True,
        "주간활동구분": "기본형",
    },
)

print(
    calculate_field(
        "본인부담금",
        {
            "등급체계구분": "산정특례",
            "월한도액": monthly_limit,
            "소득등급": "마",
        },
    )
)
print()


print("산정특례 / 2등급 / 취약가구 / 학교생활O / 직장생활X / 확장형 / 다형")
monthly_limit = calculate_field(
    "월한도액_산정특례",
    {
        "기본급여등급": 2,
        "추가특성": "2등급이하취약가구",
        "학교생활여부": True,
        "직장생활여부": False,
        "주간활동구분": "확장형",
    },
)
print(
    calculate_field(
        "본인부담금_확장형",
        {
            "등급체계구분": "산정특례",
            "월한도액": monthly_limit,
            "소득등급": "다",
        },
    )
)
print()


print("종합조사 / 8구간 / 다형")
print(
    calculate_field(
        "본인부담금",
        {
            "등급체계구분": "종합조사",
            "월한도액": CONSTANTS["월한도액"][8],
            "소득등급": "다",
        },
    )
)
print()


print("종합조사 / 4구간 / 확장형 / 다형")
print(
    calculate_field(
        "본인부담금_확장형",
        {
            "등급체계구분": "종합조사",
            "월한도액": CONSTANTS["월한도액_확장형"][8],
            "소득등급": "다",
        },
    )
)
print()


print("종합조사 / 11구간 / 나형")
print(
    calculate_field(
        "본인부담금",
        {
            "등급체계구분": "종합조사",
            "월한도액": CONSTANTS["월한도액"][11],
            "소득등급": "나",
        },
    )
)
print()


print("종합조사 / 11구간 / 확장형 / 나형")
print(
    calculate_field(
        "본인부담금_확장형",
        {
            "등급체계구분": "종합조사",
            "월한도액": CONSTANTS["월한도액"][11],
            "소득등급": "나",
        },
    )
)
print()


print("활동보조 30분 평일 단가")
print(calculate_field("활동보조30분단가"))
print()


print("활동보조 30분 심야 단가")
print(calculate_field("활동보조30분심야단가"))
print()


print("방문목욕 40분 단가 / 가정내입욕")
print(
    calculate_field(
        "방문목욕40분단가",
        {"서비스종류": "가정내입욕"},
    )
)
print()


print("방문목욕 40분 단가 / 차량내입욕")
print(
    calculate_field(
        "방문목욕40분단가",
        {"서비스종류": "차량내입욕"},
    )
)

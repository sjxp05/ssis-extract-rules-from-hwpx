from app.calc.constants import CONSTANTS
from app.calc.text_to_func import calculate_field

print(
    calculate_field("본인부담금", {"등급": "다", "월한도액": CONSTANTS["월한도액"][13]})
)
print(
    calculate_field("본인부담금", {"등급": "가", "월한도액": CONSTANTS["월한도액"][13]})
)
print(
    calculate_field("본인부담금", {"등급": "나", "월한도액": CONSTANTS["월한도액"][13]})
)
print(calculate_field("확장형본인부담금", {"등급": "나", "확장형월한도액": 5_000_000}))

print(calculate_field("활동보조30분심야"))

print(
    calculate_field(
        "방문목욕40분",
        {"방문목욕기본단가": CONSTANTS["방문목욕기본단가"]["가정내입욕"]},
    )
)
print(
    calculate_field(
        "방문목욕40분",
        {"방문목욕기본단가": CONSTANTS["방문목욕기본단가"]["차량내입욕"]},
    )
)

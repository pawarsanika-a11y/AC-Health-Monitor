from dashboard.utils.ml_inference import models_available, run_inference
from dashboard.utils.sample_data import get_current_system_state

print('Models available:', models_available())

state = get_current_system_state(
    scenario_name='Healthy Operation (Standard)',
    esp32_online=True,
)

result = run_inference(state)
print('Inference result:', result)


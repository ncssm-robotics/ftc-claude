#!/bin/bash
# Comprehensive test of calculate_gains.py

echo "===== Calculate Gains Comprehensive Test ====="
echo ""

# Test 1: Pole placement with first-order model
echo "Test 1: Pole placement (first-order model)"
python3 ../calculate_gains.py \
  --model elevator_first_order_model.json \
  --rise-time 1.0 \
  --overshoot 10 \
  --output test1_gains.json > /dev/null 2>&1

if [ $? -eq 0 ]; then
  echo "  ✅ PASS: Pole placement works"
  kP=$(jq -r '.calculated_gains.kP' test1_gains.json)
  echo "     kP = $kP"
else
  echo "  ❌ FAIL: Pole placement failed"
  exit 1
fi

# Test 2: Second-order model
echo "Test 2: Pole placement (second-order model)"
python3 ../calculate_gains.py \
  --model cable_second_order_model.json \
  --rise-time 0.8 \
  --overshoot 5 \
  --output test2_gains.json > /dev/null 2>&1

if [ $? -eq 0 ]; then
  echo "  ✅ PASS: Second-order model works"
else
  echo "  ❌ FAIL: Second-order failed"
  exit 1
fi

# Test 3: Ziegler-Nichols
echo "Test 3: Ziegler-Nichols method"
python3 ../calculate_gains.py \
  --model elevator_first_order_model.json \
  --method model-based-zn \
  --output test3_gains.json > /dev/null 2>&1

if [ $? -eq 0 ]; then
  echo "  ✅ PASS: Ziegler-Nichols works"
else
  echo "  ❌ FAIL: Ziegler-Nichols failed"
  exit 1
fi

# Test 4: Lambda tuning
echo "Test 4: Lambda tuning method"
python3 ../calculate_gains.py \
  --model elevator_first_order_model.json \
  --method lambda-tuning \
  --lambda-factor 1.5 \
  --output test4_gains.json > /dev/null 2>&1

if [ $? -eq 0 ]; then
  echo "  ✅ PASS: Lambda tuning works"
else
  echo "  ❌ FAIL: Lambda tuning failed"
  exit 1
fi

# Test 5: Output format validation
echo "Test 5: Output format validation"
required_fields=("mechanism" "synthesis_method" "calculated_gains" "predicted_performance")
all_present=true

for field in "${required_fields[@]}"; do
  if jq -e ".$field" test1_gains.json > /dev/null 2>&1; then
    continue
  else
    echo "  ❌ Missing field: $field"
    all_present=false
  fi
done

if [ "$all_present" = true ]; then
  echo "  ✅ PASS: All required fields present"
else
  echo "  ❌ FAIL: Output format incomplete"
  exit 1
fi

# Test 6: Performance predictions
echo "Test 6: Performance prediction validation"
rise_time=$(jq -r '.predicted_performance.rise_time_sec' test1_gains.json)
overshoot=$(jq -r '.predicted_performance.overshoot_percent' test1_gains.json)

if [[ -n "$rise_time" && -n "$overshoot" ]]; then
  echo "  ✅ PASS: Performance predictions present"
  echo "     Rise time: ${rise_time}s, Overshoot: ${overshoot}%"
else
  echo "  ❌ FAIL: Performance predictions missing"
  exit 1
fi

# Test 7: Error handling (missing file)
echo "Test 7: Error handling (missing file)"
python3 ../calculate_gains.py \
  --model nonexistent.json \
  --output test7_gains.json > /dev/null 2>&1

if [ $? -ne 0 ]; then
  echo "  ✅ PASS: Correctly handles missing file"
else
  echo "  ❌ FAIL: Should have failed with missing file"
  exit 1
fi

# Cleanup
rm -f test*.json

echo ""
echo "===== All Tests Passed! ====="

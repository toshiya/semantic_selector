#!/bin/zsh
export N_TEST_DATA=820,2014,2296,1133,822,2835,3232,1676,482,1702,2087,1318,839,1361,2143,1849,783,1723,595,2551,1212,2026,1935,840,3189,1873,2672,610,1525,2031,3019,222,1464,1496,2792,1194,44,3101,2884,170,1338,3245,1358,2513,3199,342,2342,375,162,1336,1956,2098,1563,1652,3106,283,1225,3211,29,674,2604,1350,661,1445,1328,1816,1080,1235,1099,1423,779,2791,3162,2238,445,874,573,461,760,2644,987,498,3096,716,1463,3044,2517,838,405,3228,2303,2145,1619,492,1240,1995,1710,1903,3171,372,3234,2013,797,258,2990,3178,688,1480,2337,347,1769,2469,3140,613,364,2294,1156,206,832,390,2378,556,3194,3170,2582,3261,2222,572,685,1241,201,1010,180,1050,1258,2573,3123,3088,2029,866,2564,682,253,737,1424,1420,3056,981,2660,2027,765,2565,671,2381,633,885,519,3231,1107,577,2480,1683,479

export PYTHONPATH=projects
export N_EPOCH=200
export BATCH_SIZE=200

[ -d result ] || mkdir result

for layers in 0 1 2 3 4 5; do
  case $layers in
    0)
      export N_UNITS_1=100
      export N_UNITS_2=30
      ;;
    1)
      export N_UNITS_1=200
      export N_UNITS_2=50
      ;;
    2)
      export N_UNITS_1=300
      export N_UNITS_2=100
      ;;
    3)
      export N_UNITS_1=500
      export N_UNITS_2=200
      ;;
    4)
      export N_UNITS_1=1000
      export N_UNITS_2=500
      ;;
    5)
      export N_UNITS_1=1000
      export N_UNITS_2=1000
      ;;
  esac

  for dropout in 0 1; do
    export DROPOUT=$dropout
    case $dropout in
      0) dr=;;
      1) dr=dropout_;;
    esac

    for relu in 0 1; do
      export RELU=$relu
      case $relu in
        0) nl=sigmoid_;;
        1) nl=relu_;;
      esac

      stem=${dr}${nl}${N_UNITS_1}_${N_UNITS_2}
      echo $stem
      if [ -f result/accuracy_${stem}.png ]; then
        :
      else
        ./projects/bin/infer_test | tee result/log_$stem.log 2>&1
        echo -n "$stem: " | tee -a result/summary.log 2>&1
        grep Accuracy result/log_$stem.log | tee -a result/summary.log 2>&1
        mv model.hdf5 result/model_${stem}.hdf5
        mv model.meta result/model_${stem}.meta
      fi
    done
  done
done

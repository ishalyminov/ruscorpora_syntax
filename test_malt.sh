if [ $# -lt 2 ]; then
    echo "Usage: test_malt.sh <text folder/file> <model file>";
    return 1;
fi

INPUT=$1;
MODEL_FILE_NAME=$2;
TRAIN_FILE_NAME=traindata.tab
MALT_RESULT_FILE_NAME=malt_result.tab

python converter.py $INPUT > $TRAIN_FILE_NAME
java -jar lib/malt.jar -c $MODEL_FILE_NAME -i $TRAIN_FILE_NAME -o $MALT_RESULT_FILE_NAME -m parse
java -jar dist-20120206/lib/MaltEval.jar  -s $MALT_RESULT_FILE_NAME -g $TRAIN_FILE_NAME

rm -f TRAIN_FILE_NAME MALT_RESULT_FILE_NAME

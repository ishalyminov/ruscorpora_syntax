if [ $# -lt 2 ]; then
    echo "Usage: train_malt.sh <text folder/file> <output file>";
    return 1;
fi

INPUT=$1;
MODEL_FILE_NAME=$2;
TRAIN_FILE_NAME=traindata.malttab

python converter.py $INPUT > $TRAIN_FILE_NAME
java -Xmx8G -jar lib/malt.jar -c $MODEL_FILE_NAME -i $TRAIN_FILE_NAME -if malttab -m learn
rm -f $TRAIN_FILE_NAME

if [ $# -lt 2 ]; then
    echo "Usage: train_malt.sh <source texts root> <output file>";
    return 1;
fi

INPUT=$1
DATASETS_FOLDER=datasets
MODEL_FILE_NAME=$2
TRAIN_FILE_NAME=train.malttab

mkdir -p $DATASETS_FOLDER
mkdir -p $DATASETS_FOLDER/corpus_converted

python syntagrus2ruscorpora.py $INPUT $DATASETS_FOLDER/corpus_converted
python disamb/create_datasets.py $DATASETS_FOLDER/corpus_converted $DATASETS_FOLDER

python converter.py $DATASETS_FOLDER/train.xml > $DATASETS_FOLDER/$TRAIN_FILE_NAME

java -Xmx8G -jar lib/malt.jar -c $MODEL_FILE_NAME -i datasets/train.malttab -if malttab -m learn

# issue: fantom words for now are denoted with '-'s
# issue: syntactic tokens can be multitokens on a single tree node
export PYTHONPATH=../../sm-photo-tool/playpen/:$PYTHONPATH
mkdir -p $1
python ./zmugfs.py -d $1

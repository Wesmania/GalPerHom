#for type in radial level brightness
for type in radial
do
  mkdir -p train/diags/$type
  for image in train/img/*.jpg
  do
    bname=$(basename $image .jpg)
    pickle=train/diags/$type/$bname.p
    python3 src/write_diagram.py --input-file $image --output-file $pickle --type $type
  done
done

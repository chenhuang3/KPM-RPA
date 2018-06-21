
read -p "System 1 or system 2? [type 1 or 2]: " system_index
read -p "Enter number of runs to submit: " nsys

for (( s = 1; s <= $nsys; s++ )) 
do 
  cd  system$system_index\_kpm_$s/
  echo ""
  echo "enter folder: "
  pwd
  sbatch -J sys$system_index\_$s job.s 
  cd ..
done 

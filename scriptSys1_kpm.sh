
read -p "Enter Number of run to submit: " nsys

for ((s = 2; s <= $nsys; s++))
do
    myval=`echo "$s * 111" | bc`
    rm -rf system1_kpm_$s
    cp -rf system1_kpm_1/ system1_kpm_$s 
    perl -i -pe 's/.*/'$myval'   !random seed / if $.==2' ./system1_kpm_$s/rpa_kpm.ini
    perl -i -pe 's/.*/#SBATCH -J \"kpm_RPA_sys1_'$s'\" / if $.==2' ./system1_kpm_$s/job.s
    echo "Submit system1_kpm_$s/job.s"
    sbatch system1_kpm_$s/job.s
done

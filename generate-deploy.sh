date
terraform graph | dot -Tsvg > tf.svg

# Create the plan (Output goes into output_plan.txt)
terraform plan -no-color -out tfplan.plan >output_plan.txt 2>&1  

# Apply the plan (Output goes into output_apply.txt)
terraform apply -no-color tfplan.plan >output_apply.txt 2>&1                                                                                          

terraform output -raw tls_private_key > id_rsa

chmod 600 id_rsa 

date

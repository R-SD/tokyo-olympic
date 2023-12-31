# Databricks notebook source

display(dbutils.secrets.listScopes())
display(dbutils.secrets.list("tokyoOlympics"))

client_id = dbutils.secrets.get(scope= "tokyoOlympics" , key="client-id")
client_secret = dbutils.secrets.get(scope= "tokyoOlympics" , key="client-secret")
tenant_id = dbutils.secrets.get(scope= "tokyoOlympics" , key="tenant-id")
configs = {"fs.azure.account.auth.type": "OAuth",
"fs.azure.account.oauth.provider.type": "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
"fs.azure.account.oauth2.client.id": client_id,
"fs.azure.account.oauth2.client.secret": client_secret,
"fs.azure.account.oauth2.client.endpoint": f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"}

display(configs)


# COMMAND ----------

dbutils.fs.mount(
source = "abfss://tokyoolympicdata@tokyoolympicreha.dfs.core.windows.net/", # contrainer@storageacc
mount_point = "/mnt/tokyoolymic/",   extra_configs = configs 
)



# COMMAND ----------

# MAGIC %fs
# MAGIC ls "/mnt/tokyoolymic/"

# COMMAND ----------

athletes = spark.read.format("csv").option("header","true").option("inferSchema","true").load("/mnt/tokyoolymic/raw_data/atheletes.csv")
athletes=athletes.withColumnRenamed("PersonName","Person_Name") #Rename column
athletes.show()
athletes.repartition(1).write.mode("overwrite").option("header",'true').csv("/mnt/tokyoolymic/transformed_data/athletes")

# COMMAND ----------


coaches = spark.read.format("csv").option("header","true").option("inferSchema","true").load("/mnt/tokyoolymic/raw_data/coaches.csv")
coaches.show()
coaches.repartition(1).write.mode("overwrite").option("header","true").csv("/mnt/tokyoolymic/transformed_data/coaches")

# COMMAND ----------

from pyspark.sql.functions import col
from pyspark.sql.types import IntegerType
entriesgender = spark.read.format("csv").option("header","true").option("inferSchema","true").load("/mnt/tokyoolymic/raw_data/entriesgender.csv")
entriesgender.show()
entriesgender=entriesgender.withColumn("Female",col("Female").cast(IntegerType()))\
    .withColumn("Male",col("Male").cast(IntegerType()))\
        .withColumn("Total",col("Total").cast(IntegerType()))
entriesgender.printSchema()                
entriesgender.repartition(1).write.mode("overwrite").option("header","true").csv("/mnt/tokyoolymic/transformed_data/entriesgender")

# COMMAND ----------

medals = spark.read.format("csv").option("header","true").option("inferSchema","true").load("/mnt/tokyoolymic/raw_data/medals.csv")
medals=medals.withColumnRenamed("Rank By Total","Rank_By_Total")
medals.show()
medals.repartition(1).write.mode("overwrite").option("header","true").csv("/mnt/tokyoolymic/transformed_data/medals")

# COMMAND ----------

teams = spark.read.format("csv").option("header","true").option("inferSchema","true").load("/mnt/tokyoolymic/raw_data/teams.csv")
teams.show()
teams.repartition(1).write.mode("overwrite").option("header","true").csv("/mnt/tokyoolymic/transformed_data/teams")

# COMMAND ----------

dbutils.fs.unmount("/mnt/tokyoolymic/")

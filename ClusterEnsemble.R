rm(list=ls())

to.similarity.matrix <- function(data) {
	len = length(data)
	smatrix=mat.or.vec(len, len)
	for (i in 1:len-1) {
		smatrix[i,i]=1
		for (j in i+1:len) {
			if (identical(data[i],data[j])) {
				smatrix[i,j]=1
				smatrix[j,i]=1	
			}
		}
	}
	smatrix[len,len]=1
	return(smatrix);
}

to.cluster.vector <- function(smatrix) {
	len = dim(smatrix)[1]
	cvector = mat.or.vec(len, 1)
	cluster = 1
	for (i in 1:len) {
		if (cvector[i]==0) {
			cvector[i] <- cluster
			if ((len-i) > 0) {
				temp = tail(smatrix[i,],len-i)
				temp_len = length(temp)
				for (j in 1:temp_len) {
					if (temp[j]==1) {
						cvector[i+j]=cluster
					}
				}
			}
			cluster = cluster + 1
		}
	}
	return(cvector)
}

round.similarity.matrix <- function(smatrix, threshold) {
	smatrix[smatrix < threshold] <- 0
	smatrix[smatrix >= threshold] <- 1
	return(smatrix)
}


featureFile <- "F:\\clustering\\mo\\output\\feature.csv"
clusterFile <- "F:\\clustering\\mo\\output\\cluster.csv"

clusterFileColNames <- c("CellID","Cluster")

# Prepare data
mydata = read.csv(featureFile)
mydata.features = mydata
mydata.features$CellID <- NULL

# Remove Inf from Data
mydata.features[is.infinite(as.matrix(mydata.features))] <- 100

mydata.clusters = 3
round.threshold = 0.5
cluster.method = 5

# K-Means Clustering
fit <- kmeans(mydata.features, mydata.clusters)
smatrix1 = to.similarity.matrix(fit$cluster)


# Ward Hierarchical Clustering
d <- dist(mydata.features)
fit <- hclust(d)
groups <- cutree(fit, k=mydata.clusters)
smatrix2 = to.similarity.matrix(groups)


# Model Based Clustering
library(mclust)
fit <- Mclust(mydata.features)
smatrix3 = to.similarity.matrix(fit$classification)


# DBSCAN
library(fpc)
fit <- dbscan(mydata.features, 0.2)
smatrix4 = to.similarity.matrix(fit$cluster)


# CLARANS
library(cluster)
fit <- clara(mydata.features, mydata.clusters)
smatrix5 = to.similarity.matrix(fit$clustering)


# Clustering Ensemble
smatrix = (smatrix1 + smatrix2 + smatrix3 + smatrix4 + smatrix5)/cluster.method

# Round to Integer
smatrix = round.similarity.matrix(smatrix, round.threshold)

# Convert to Clustering Vector
cvector = to.cluster.vector(smatrix)

clusterResult <- cbind(mydata$CellID,cvector)
write.table(clusterResult,file=clusterFile,sep=',',col.names=clusterFileColNames,row.names=FALSE,quote=FALSE)

library(ggplot2)
library(dplyr)
library(fmsb)
library(tidyverse)
library(svglite)
library(gdtools)

rm(list=ls())
par(mfrow=c(2,2),mar=c(4,1,4,1), oma=c(1,0,1,0))

setwd("~/Documents/spotify-hacks")

df<-read.csv("exports/artistProfile.csv",row.names=1)

df<-rbind(rep(1,10),rep(0,10),df)
cols=c(2,3,4,5,6,7,9)
df<-df[,cols]
df
# Radar chart
colors_border <- c( rgb(0.2,0.5,0.5,0.9), rgb(0.8,0.2,0.5,0.9), rgb(0.7,0.5,0.1,0.9))
colors_in <- c( rgb(0.2,0.5,0.5,0.4), rgb(0.8,0.2,0.5,0.4), rgb(0.7,0.5,0.1,0.4))

dfAve <- c(apply(df,2,median))
df[nrow(df)+1,]=dfAve

for (index in seq(3,nrow(df)-1)){
  
  rows<-c(1,2,nrow(df),index)
  
  svg(filename=paste("artistDistribution/",rownames(df[index,]),"/",rownames(df[index,])," profile.svg",sep=""), 
      width=6, 
      height=6, 
      pointsize=10)
  
  radarchart(df[rows,], 
             axistype=1 , 
             #customize the polygons
             pcol=colors_border, 
             pfcol=colors_in, 
             plwd=2, 
             plty=1,
             pty=32,
             #customize the grid
             cglcol="grey", 
             cglty=1, 
             axislabcol="black", 
             caxislabels=seq(0,1,5), 
             cglwd=0.5,
             #custom labels
             vlcex=0.7,
             calcex=0.8,
             title=rownames(df[index,]))
  
  legend("topright",
         legend=c("Average Artist",rownames(df[index,])),
         col=colors_in,
         pt.cex=2.5,
         pch=16,
         bty="n",
         cex=1,
         text.col="black"
  )
  
  dev.off()
  
}
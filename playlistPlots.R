library(ggplot2)
library(dplyr)
library(fmsb)
library(tidyverse)
library(svglite)
library(gdtools)
par(mfrow=c(2,2),mar=c(4,1,4,1), oma=c(1,0,1,0))

setwd("~/Documents/spotify-hacks")

df<-read.csv("playlistViz.csv",row.names=1)

df<-rbind(rep(1,9),rep(0,9),df)
# Radar chart
colors_border <- c( rgb(0.2,0.5,0.5,0.9), rgb(0.8,0.2,0.5,0.9), rgb(0.7,0.5,0.1,0.9))
colors_in <- c( rgb(0.2,0.5,0.5,0.4), rgb(0.8,0.2,0.5,0.4), rgb(0.7,0.5,0.1,0.4))

for (index in seq(3,nrow(df))){
  rows<-c(1,2,index)
  svg(filename=paste("plots/",rownames(df[index,]),".svg",sep=""), 
      width=5, 
      height=4, 
      pointsize=8)
  
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
             axislabcol="grey", 
             caxislabels=seq(0,1,5), 
             cglwd=0.5,
             #custom labels
             vlcex=0.48,
             calcex=0.5,
             title=rownames(df[index,])) 
             dev.off()
}
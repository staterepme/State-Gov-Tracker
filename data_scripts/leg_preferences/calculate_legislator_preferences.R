# Calculate Ideal Points of Legislators
library("RSQLite")
library("pscl")
library("ggplot2")

# Load Data 
# Path to SQLite Database #
conn <- dbConnect("SQLite", dbname = "/home/christopher/Dropbox/CongressMonitor/StateGovTracker.db")

# Get Votes Table
votes <- dbReadTable(conn, "pa_legis_votes")
vote_sub <- votes[,1:3]

# Get Member Table
mem_info <- dbReadTable(conn, "officials")
mem_data <- data.frame(cbind(mem_info$legid, mem_info$party, mem_info$chamber), stringsAsFactors = FALSE)

lower_mem <- subset(mem_data, X3 %in% c("lower"))
upper_mem <- subset(mem_data, X3 %in% c("upper"))

lower_legid <- lower_mem[1]
upper_legid <- upper_mem[1]

# Reshape Votes so that each row is a legislator and column is a vote
votes_wide <- reshape(vote_sub, idvar="legid", timevar="bill_id", direction="wide")

# Create Roll Call Vote Object #
colnames(votes_wide)[1] <- "legis.names"
length(colnames(votes_wide))

# Separate out Upper and Lower Chambers #
upper_wide <- subset(votes_wide, legis.names %in% c(upper_legid$X1))
lower_wide <- subset(votes_wide, legis.names %in% c(lower_legid$X1))
upper_vote_wide_sub <- upper_wide[,2:1378]
lower_vote_wide_sub <- lower_wide[,2:1378]

# Create Roll Call Objects (drop legislators with less than 5 votes and drop votes with less than 5 in opposition)
rc_upper <- rollcall(upper_vote_wide_sub, missing=c(NA, 99), legis.names=upper_wide[,1])
rc_lower <- rollcall(lower_vote_wide_sub, missing=c(NA, 99), legis.names=lower_wide[,1])

rc_upper_fixed <- dropRollCall(rc_upper, dropList=list(lop=5, legisMin=5))
rc_lower_fixed <- dropRollCall(rc_lower, dropList=list(lop=5, legisMin=5))
summary(rc_upper_fixed)

# Calculate Ideal Points #
id1 <- ideal(rc_upper_fixed,
             d=1,
             startvals="eigen",
             normalize=TRUE,
             store.item=TRUE,
             maxiter=100000,
             burnin=10000,
             thin=100,
             verbose=TRUE)  

id2 <- ideal(rc_lower_fixed,
             d=1,
             startvals="eigen",
             normalize=TRUE,
             store.item=TRUE,
             maxiter=100000,
             burnin=10000,
             thin=100,
             verbose=TRUE)

# Combine Ideal Points with Party Data #
ideal_scores_upper <- cbind(upper_wide[,1], id1$xbar)
ideal_scores_upper <- data.frame(ideal_scores_upper, row.names=NULL)
ideal_scores_lower <- cbind(lower_wide[,1], id2$xbar)
ideal_scores_lower <- data.frame(ideal_scores_lower, row.names=NULL)

# Transform Variables into correct formats
ideal_scores_upper$D1 <- as.numeric(levels(ideal_scores_upper$D1))[ideal_scores_upper$D1]
combined_upper <- merge(upper_mem, ideal_scores_upper, by.x = "X1", by.y = "V1")
ideal_scores_lower$D1 <- as.numeric(levels(ideal_scores_lower$D1))[ideal_scores_lower$D1]
combined_lower <- merge(lower_mem, ideal_scores_lower, by.x = "X1", by.y = "V1")

combined_upper$X2 <- as.factor(combined_upper$X2)
combined_upper$X3 <- as.factor(combined_upper$X3)
combined_lower$X2 <- as.factor(combined_lower$X2)
combined_lower$X3 <- as.factor(combined_lower$X3)

combined <- rbind(combined_upper, combined_lower)

for (i in 1:length(combined$D1)) {
    combined$D1[i] <- -1*combined$D1[i]
}

# Generate Kernel Density Plots #
dist <- ggplot(combined, aes(x=D1)) + geom_density(alpha=.2, fill="#FF6666") 
dist + facet_grid(X2 ~ X3)

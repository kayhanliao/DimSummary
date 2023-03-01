## Description 

Each review is concatenated by restaurant and partitioned by restaurant.  Since max input size of chatgpt is around 10240 chars,give or take, we're limiting the each concatenation to around that amount. 

## Steps

1. copy text of a row that has not been labeled yet. 
2. type the following to chat "use the following opinions of the restaurant reviews to create a 50 word summary" and paste the copied review text
3. copy paste the outputs into the same rows summary column in the csv file
4. repeat 1-3

if there's any issues, skip that row and move on, or msg me.

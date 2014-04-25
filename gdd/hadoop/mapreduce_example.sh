#### Mapreduce Example
echo "foo foo quux labs foo bar quux" | /home/hduser/stream_examples/wordcount/mapper.py | sort -k1,1 | /home/hduser/stream_examples/wordcount/reducer.py

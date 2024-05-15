#!/bin/bash

# TODO: the lookup in this array is super slow... 
ARRAY=(

cd $TCO

for f in */*/*.pcap
do
  OLD_F=$f
  FULL_ONION=$(echo $f | sed -n "s/.*\/\(.*\)\/.*.pcap/\1/p")
  if [ "$FULL_ONION" = "full-onion" ]
  then
    OS_PAGE=$(echo $f | sed -n "s/.*\/full-onion\/.*_\(.*\)_hs.pcap/\1/p")
    for onion_pages in "${ARRAY[@]}"
    do
      KEY=${onion_pages%%:*}
      VALUE=${onion_pages#*:}
      if [ "$KEY" = "$OS_PAGE" ]
      then
        break
      fi
    done
    NEW_F=$(echo $f | sed -n "s/\(.*\)\/full-onion\/\(.*\)/${VALUE}-\1\/full-onion\/\2/p")
    # echo "$OLD_F > $NEW_F"
    mkdir -p $(dirname $NEW_FOLDER/$NEW_F)
    cp $OLD_F $NEW_FOLDER/$NEW_F
  else
    OS_PAGE=$(echo $f | sed -n "s/.*\/.*\/.*new_\(.*\)_session.*/\1/p")
    for onion_pages in "${ARRAY[@]}"
    do
      KEY=${onion_pages%%:*}
      VALUE=${onion_pages#*:}
      if [ "$KEY" = "$OS_PAGE" ]
      then
        break
      fi
    done
    # echo $OS_PAGE - $VALUE
    NEW_F=$(echo $f | sed -n "s/\(.*\)-new-\(.*\)-os-\(.*\)\/\(.*\)\/\(.*\)-new_os-\(.*\)/\1-new-\2-${VALUE}-os-\3\/\4\/\5-new-\2_${VALUE}-os-\6/p")
    # echo $OS_PAGE
    # echo "$OLD_F > $NEW_F"
    mkdir -p $(dirname $NEW_FOLDER/$NEW_F)
    cp $OLD_F $NEW_FOLDER/$NEW_F
  fi
done
---
title: "$title$"
$if(subtitle)$subtitle: "$subtitle$"
$endif$$if(author)$author: "$for(author)$$author$$sep$, $endfor$"
$endif$$if(date)$date: "$date$"
$endif$---

# $title$

$if(subtitle)$*$subtitle$*
$endif$
$if(author)$$for(author)$$author$$sep$, $endfor$$if(date)$ · $date$$endif$
$endif$
$if(toc)$
## Contents

$table-of-contents$
$endif$

$body$

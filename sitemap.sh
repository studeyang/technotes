#!/bin/bash

sitemap="sitemap.xml"
website_link="https://studeyang.tech/technotes"
ignore=(
  sidebar.md
  A类/Python/sidebar.md
  B类/sidebar.md
  C类/sidebar.md
  D类/sidebar.md
  README.md
  A类/Python/README.md
  A类/README.md
  B类/README.md
  C类/README.md
  D类/README.md
  coverpage.md
  navbar.md
)

urlencode() {
  local length="${#1}"
  for ((i = 0; i < length; i++)); do
    local c="${1:i:1}"
    case $c in
    [a-zA-Z0-9.~_+-/]) printf "$c" ;;
    *) printf "$c" | xxd -p -c1 | while read x; do printf "%%%s" "$x"; done ;;
    esac
  done
}
files=$(
  git ls-files -z '*.md' |
    xargs -0 -n1 -I{} -- git log -1 --format="%at {}" {} |
    sort -r |
    cut -d " " -f2-
)

items=""
for file in ${files[@]}; do
  [[ ${ignore[@]/${file}/} != ${ignore[@]} ]] && continue
  echo $file
  encode=$(urlencode "${file::-3}")
  link="$website_link/#/$encode"
  date=$(git log -1 --format="%ad" --date="iso-strict-local" -- $file)
  item="
  <url>
    <loc>$link</loc>
    <lastmod>$date</lastmod>
  </url>
  "
  items="$items $item"
done

now=$(git log -1 --format="%ad" --date="iso-strict-local")
sitemap_content="<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">
  <url>
    <loc>$website_link</loc>
    <lastmod>$now</lastmod>
  </url>
  $items
</urlset>"

echo "$sitemap_content" >$sitemap

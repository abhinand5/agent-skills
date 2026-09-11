-- LaTeX cannot include SVG directly. For the PDF build, convert every SVG image
-- to PDF with rsvg-convert (into build/figures/) and point the include at it.
-- Other formats keep the SVG, which reflows and stays crisp on e-readers.

if not FORMAT:match("latex") then
  return {}
end

local out_dir = os.getenv("BUILD_DIR") or "build"
os.execute("mkdir -p '" .. out_dir .. "/figures'")

function Image(img)
  if not img.src:match("%.svg$") then return nil end
  local base = img.src:gsub("^.*/", ""):gsub("%.svg$", "")
  local target = out_dir .. "/figures/" .. base .. ".pdf"
  local ok = os.execute("rsvg-convert --format=pdf --output='" .. target .. "' '" .. img.src .. "'")
  if not ok then
    error("svg-figures.lua: rsvg-convert failed for " .. img.src)
  end
  img.src = target
  return img
end

-- Book structure for every output format.
--
-- * Numbers chapters/sections for EPUB and Markdown (LaTeX numbers itself).
-- * A raw `\appendix` line switches to Appendix A, B, ... numbering.
-- * Raw LaTeX page breaks are dropped outside LaTeX.
-- * Divs with class printonly / epubonly / mdonly appear only in that edition.

local is_latex = FORMAT:match("latex") ~= nil
local is_markdown = FORMAT:match("markdown") ~= nil or FORMAT:match("gfm") ~= nil
  or FORMAT:match("commonmark") ~= nil
local is_epub = not is_latex and not is_markdown

local chapter = 0
local appendix = 0
local section = 0
local in_appendix = false
local current = nil

local function has_class(el, name)
  for _, c in ipairs(el.classes) do
    if c == name then return true end
  end
  return false
end

local function label_span(text, block)
  local classes = { "heading-number" }
  if block then table.insert(classes, "heading-number-block") end
  return pandoc.Span({ pandoc.Str(text) }, pandoc.Attr("", classes, {}))
end

function RawBlock(raw)
  if raw.format ~= "latex" and raw.format ~= "tex" then return nil end
  local text = raw.text:gsub("%s+$", "")
  if text == "\\appendix" then
    in_appendix = true
    if is_latex then return nil end
    return {}
  end
  if text == "\\newpage" or text == "\\clearpage" or text == "\\cleardoublepage" then
    if is_latex then return nil end
    return {}
  end
  return nil
end

function Div(div)
  if has_class(div, "printonly") then
    if is_latex then return div.content end
    return {}
  end
  if has_class(div, "epubonly") then
    if is_epub then return div.content end
    return {}
  end
  if has_class(div, "mdonly") then
    if is_markdown then return div.content end
    return {}
  end
  return nil
end

-- Markdown edition: keep it portable. Figures become plain image paragraphs and
-- citeproc's HTML reference divs become ordinary paragraphs.
function Figure(fig)
  if not is_markdown then return nil end
  local first = fig.content[1]
  if first and (first.t == "Plain" or first.t == "Para") and first.content[1] and first.content[1].t == "Image" then
    local img = first.content[1]
    img.caption = fig.caption.long[1] and fig.caption.long[1].content or img.caption
    return pandoc.Para({ img })
  end
  return nil
end

local flatten_markdown_refs = {
  Div = function(div)
    if not is_markdown then return nil end
    if has_class(div, "csl-entry") then
      local inlines = pandoc.Inlines({})
      for _, block in ipairs(div.content) do
        if block.t == "Para" or block.t == "Plain" then
          inlines:extend(block.content)
        end
      end
      return pandoc.Para(inlines)
    end
    if div.identifier == "refs" then
      return div.content
    end
    return nil
  end,
  Span = function(span)
    if not is_markdown then return nil end
    if has_class(span, "csl-left-margin") or has_class(span, "csl-right-inline") then
      return span.content
    end
    return nil
  end,
}

function Header(h)
  if is_latex then return nil end
  if has_class(h, "unnumbered") then
    if h.level == 1 then current = nil end
    return nil
  end
  if h.level == 1 then
    section = 0
    if in_appendix then
      appendix = appendix + 1
      current = string.char(64 + appendix)
      if is_markdown then
        h.content:insert(1, pandoc.Str("Appendix " .. current .. ". "))
      else
        h.content:insert(1, pandoc.Space())
        h.content:insert(1, label_span("Appendix " .. current, true))
      end
    else
      chapter = chapter + 1
      current = tostring(chapter)
      if is_markdown then
        h.content:insert(1, pandoc.Str("Chapter " .. current .. ". "))
      else
        h.content:insert(1, pandoc.Space())
        h.content:insert(1, label_span("Chapter " .. current, true))
      end
    end
    return h
  end
  if h.level == 2 and current then
    section = section + 1
    local label = current .. "." .. tostring(section)
    if is_markdown then
      h.content:insert(1, pandoc.Str(label .. " "))
    else
      h.content:insert(1, pandoc.Space())
      h.content:insert(1, label_span(label, false))
    end
    return h
  end
  return nil
end

return {
  { RawBlock = RawBlock, Div = Div, Header = Header, Figure = Figure },
  flatten_markdown_refs,
}

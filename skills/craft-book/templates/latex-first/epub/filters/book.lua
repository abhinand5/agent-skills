-- Adapt the print-oriented LaTeX AST to a compact, reflowable EPUB.
--
-- * Numbers chapters/sections (pandoc does not number LaTeX-derived headings).
-- * Turns \cite{key} into [n] links and \bibitem entries into anchored [n] paragraphs.
--   The key order is read from backmatter/bibliography.tex, so nothing is hard-coded.
-- * Adds the box titles that tcolorbox supplied in print.
-- * Drops the print title page; unwraps `epubonly` blocks.

local bibliography_path = os.getenv("BIBLIOGRAPHY") or "backmatter/bibliography.tex"

local references = {}
do
  local handle = io.open(bibliography_path)
  if not handle then
    error("book.lua: cannot read " .. bibliography_path)
  end
  for line in handle:lines() do
    local key = line:match("^%s*\\bibitem{([^}]+)}")
    if key then
      table.insert(references, key)
    end
  end
  handle:close()
end

local reference_number = {}
for index, key in ipairs(references) do
  reference_number[key] = index
end

-- tcolorbox environments and their print titles (keep in sync with style.tex).
local box_titles = {
  mentalmodel = "Mental model",
  failuremode = "Failure mode",
  checkpoint = "Checkpoint",
  takeaway = "What survives",
  -- amsthm `example` already carries "Example n.m", so it gets no extra title.
}

local chapter_number, appendix_number, section_number = 0, 0, 0
local current_kind, current_number = nil, nil

local function has_class(element, class_name)
  for _, class in ipairs(element.classes) do
    if class == class_name then return true end
  end
  return false
end

local function prepend_heading_number(header, label, block_style)
  local classes = { "heading-number" }
  if block_style then table.insert(classes, "heading-number-block") end
  header.content:insert(1, pandoc.Space())
  header.content:insert(1, pandoc.Span({ pandoc.Str(label) }, pandoc.Attr("", classes, {})))
  return header
end

function Header(header)
  if header.level == 1 then
    section_number = 0
    if header.identifier:match("^ch:") then
      chapter_number = chapter_number + 1
      current_kind, current_number = "chapter", tostring(chapter_number)
      return prepend_heading_number(header, "Chapter " .. current_number, true)
    elseif header.identifier:match("^app:") then
      appendix_number = appendix_number + 1
      current_kind, current_number = "appendix", string.char(64 + appendix_number)
      return prepend_heading_number(header, "Appendix " .. current_number, true)
    else
      current_kind, current_number = nil, nil
    end
  elseif header.level == 2 and current_kind and not has_class(header, "unnumbered") then
    section_number = section_number + 1
    return prepend_heading_number(header, current_number .. "." .. tostring(section_number), false)
  end
  return header
end

function Cite(citation)
  local result = pandoc.Inlines({ pandoc.Str("[") })
  for index, item in ipairs(citation.citations) do
    local number = reference_number[item.id]
    if not number then
      error("Unknown citation key in EPUB build: " .. item.id)
    end
    if index > 1 then
      result:insert(pandoc.Str(","))
      result:insert(pandoc.Space())
    end
    result:insert(pandoc.Link({ pandoc.Str(tostring(number)) }, "#ref-" .. item.id, "Reference " .. tostring(number)))
  end
  result:insert(pandoc.Str("]"))
  return result
end

local function box_title_block(title)
  return pandoc.Plain({ pandoc.Span({ pandoc.Str(title) }, pandoc.Attr("", { "box-title" }, {})) })
end

local function bibliography_blocks(div)
  local blocks = pandoc.Blocks({
    pandoc.Header(1, { pandoc.Str("References") }, pandoc.Attr("references", { "unnumbered" }, {})),
  })
  -- Pandoc keeps the width argument of \begin{thebibliography}{99} as the first paragraph.
  local entry_index = 0
  for source_index, block in ipairs(div.content) do
    if source_index > 1 then
      entry_index = entry_index + 1
      local key = references[entry_index]
      if not key then
        error("The EPUB bibliography has more entries than " .. bibliography_path)
      end
      if block.t == "Para" or block.t == "Plain" then
        block.content:insert(1, pandoc.Space())
        block.content:insert(1, pandoc.Span({ pandoc.Str("[" .. tostring(entry_index) .. "]") },
          pandoc.Attr("", { "reference-number" }, {})))
      end
      blocks:insert(pandoc.Div({ block }, pandoc.Attr("ref-" .. key, { "reference" }, {})))
    end
  end
  if entry_index ~= #references then
    error("bibliography has " .. #references .. " \\bibitem keys but " .. entry_index .. " parsed entries")
  end
  return blocks
end

function Div(div)
  if has_class(div, "titlepage") then
    return {}
  end
  if has_class(div, "thebibliography") then
    return bibliography_blocks(div)
  end
  if has_class(div, "epubonly") then
    return div.content
  end
  if has_class(div, "rlalgorithm") or has_class(div, "algorithm") then
    local title = "Algorithm"
    local first_block = div.content[1]
    if first_block and first_block.t == "Para" then
      local first_inline = first_block.content[1]
      if first_inline and first_inline.t == "Span" then
        title = pandoc.utils.stringify(first_inline)
        first_block.content:remove(1)
        if first_block.content[1] and first_block.content[1].t == "SoftBreak" then
          first_block.content:remove(1)
        end
      end
    end
    div.content:insert(1, box_title_block(title))
    return div
  end
  for class_name, title in pairs(box_titles) do
    if has_class(div, class_name) then
      div.content:insert(1, box_title_block(title))
      return div
    end
  end
  return div
end

-- Markdown edition of a LaTeX-first book: turn the EPUB-oriented AST into portable Markdown.
-- Runs after book.lua. Box titles become bold lines inside blockquotes; figures become
-- plain images; heading-number spans become text; epub asset paths are rewritten.

local box_classes = { "mentalmodel", "failuremode", "checkpoint", "takeaway", "example", "algorithm", "reference" }

local function has_class(el, name)
  for _, c in ipairs(el.classes) do if c == name then return true end end
  return false
end

function Div(div)
  for _, class in ipairs(box_classes) do
    if has_class(div, class) then
      if class == "reference" then
        return div.content
      end
      local blocks = pandoc.Blocks({})
      for i, block in ipairs(div.content) do
        if i == 1 and block.t == "Plain" and block.content[1] and block.content[1].t == "Span"
          and has_class(block.content[1], "box-title") then
          blocks:insert(pandoc.Para({ pandoc.Strong(block.content[1].content) }))
        else
          blocks:insert(block)
        end
      end
      return pandoc.BlockQuote(blocks)
    end
  end
  return nil
end

function Span(span)
  if has_class(span, "heading-number") or has_class(span, "reference-number") or has_class(span, "box-title") then
    return span.content
  end
  return nil
end

function Figure(fig)
  local first = fig.content[1]
  if first and (first.t == "Plain" or first.t == "Para") and first.content[1] and first.content[1].t == "Image" then
    local img = first.content[1]
    img.caption = fig.caption.long[1] and fig.caption.long[1].content or img.caption
    return pandoc.Para({ img })
  end
  return nil
end

function Image(img)
  img.src = img.src:gsub("^epub/assets/", "assets/")
  -- GFM cannot carry attributes; without this the writer falls back to raw <img> HTML.
  if #img.caption == 0 and img.attributes["alt"] then
    img.caption = pandoc.Inlines({ pandoc.Str(img.attributes["alt"]) })
  end
  img.attr = pandoc.Attr()
  return img
end

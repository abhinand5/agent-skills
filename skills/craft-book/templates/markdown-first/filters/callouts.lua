-- Map fenced-div callouts to each output format.
--
--   ::: mentalmodel      ::: failuremode     ::: checkpoint
--   ::: takeaway         ::: example         ::: {.algorithm title="Value iteration"}
--
-- LaTeX  -> tcolorbox environments defined in pdf/preamble.tex
-- EPUB   -> <div class="..."> with an injected bold title line (styled by epub/kindle.css)
-- GFM    -> blockquote with a bold title line, so the Markdown edition reads well on GitHub

local titles = {
  mentalmodel = "Mental model",
  failuremode = "Failure mode",
  checkpoint = "Checkpoint",
  takeaway = "What survives",
  example = "Worked example",
  algorithm = "Algorithm",
}

local function callout_class(div)
  for _, class in ipairs(div.classes) do
    if titles[class] then
      return class
    end
  end
  return nil
end

local function title_for(div, class)
  return div.attributes["title"] or titles[class]
end

function Div(div)
  local class = callout_class(div)
  if not class then
    return nil
  end
  local title = title_for(div, class)

  if FORMAT:match("latex") then
    local env = class
    local open = "\\begin{" .. env .. "}"
    if class == "algorithm" or div.attributes["title"] then
      open = open .. "[" .. title .. "]"
    end
    local blocks = pandoc.Blocks({ pandoc.RawBlock("latex", open) })
    blocks:extend(div.content)
    blocks:insert(pandoc.RawBlock("latex", "\\end{" .. env .. "}"))
    return blocks
  end

  if FORMAT:match("markdown") or FORMAT:match("gfm") or FORMAT:match("commonmark") then
    local blocks = pandoc.Blocks({ pandoc.Para({ pandoc.Strong({ pandoc.Str(title) }) }) })
    blocks:extend(div.content)
    return pandoc.BlockQuote(blocks)
  end

  -- EPUB / HTML
  div.content:insert(1, pandoc.Plain({
    pandoc.Span({ pandoc.Str(title) }, pandoc.Attr("", { "box-title" }, {})),
  }))
  return div
end

"use client";

import React, { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import type { Components } from "react-markdown";
import {
  Check,
  Copy,
  Info,
  Lightbulb,
  AlertTriangle,
  AlertCircle,
  Zap,
  TrendingUp,
  ExternalLink,
} from "lucide-react";



interface ChatMarkdownProps {
  content: string;
  streaming?: boolean;
}




function normalizeContent(content: string, streaming?: boolean): string {
  if (!streaming) return content;
  const fences = (content.match(/^```/gm) ?? []).length;
  if (fences % 2 !== 0) return content + "\n```";
  return content;
}



const lexaraTheme: Record<string, React.CSSProperties> = {
  'code[class*="language-"]': {
    color: "#cdd6f4",
    fontFamily: "var(--font-mono, ui-monospace, monospace)",
    fontSize: "0.83em",
    lineHeight: "1.7",
    background: "none",
    textShadow: "none",
  },
  'pre[class*="language-"]': {
    color: "#cdd6f4",
    background: "transparent",
    margin: 0,
    padding: 0,
    overflow: "auto",
  },
  comment: { color: "#585b70", fontStyle: "italic" },
  prolog: { color: "#585b70" },
  doctype: { color: "#585b70" },
  cdata: { color: "#585b70" },
  punctuation: { color: "#cdd6f4" },
  namespace: { opacity: 0.7 },
  property: { color: "#89dceb" },
  tag: { color: "#f38ba8" },
  boolean: { color: "#fab387" },
  number: { color: "#fab387" },
  constant: { color: "#cba6f7" },
  symbol: { color: "#f38ba8" },
  deleted: { color: "#f38ba8" },
  selector: { color: "#a6e3a1" },
  "attr-name": { color: "#cba6f7" },
  string: { color: "#a6e3a1" },
  char: { color: "#a6e3a1" },
  builtin: { color: "#89dceb" },
  inserted: { color: "#a6e3a1" },
  operator: { color: "#89dceb" },
  entity: { color: "#f9e2af", cursor: "help" },
  url: { color: "#89dceb" },
  variable: { color: "#cdd6f4" },
  atrule: { color: "#cba6f7" },
  "attr-value": { color: "#a6e3a1" },
  function: { color: "oklch(0.85 0.16 200)", fontWeight: "500" },
  "class-name": { color: "#f9e2af" },
  keyword: { color: "oklch(0.72 0.22 290)", fontWeight: "600" },
  regex: { color: "#f9e2af" },
  important: { color: "#f38ba8", fontWeight: "bold" },
};



const LANG_COLORS: Record<string, string> = {
  js: "#f7df1e",
  javascript: "#f7df1e",
  ts: "#3178c6",
  typescript: "#3178c6",
  python: "#3572A5",
  py: "#3572A5",
  rust: "#CE422B",
  go: "#00ADD8",
  java: "#B07219",
  css: "#563d7c",
  html: "#e34c26",
  bash: "#89e051",
  sh: "#89e051",
  shell: "#89e051",
  sql: "#336791",
  json: "#292929",
  yaml: "#cb171e",
  yml: "#cb171e",
  markdown: "#083fa1",
  md: "#083fa1",
  cpp: "#f34b7d",
  c: "#555555",
  text: "#888888",
};



const CALLOUTS = {
  NOTE: { Icon: Info, label: "Note", cls: "callout-note" },
  TIP: { Icon: Lightbulb, label: "Tip", cls: "callout-tip" },
  WARNING: { Icon: AlertTriangle, label: "Warning", cls: "callout-warning" },
  CAUTION: { Icon: AlertCircle, label: "Caution", cls: "callout-caution" },
  IMPORTANT: { Icon: Zap, label: "Important", cls: "callout-important" },
} as const;

type CalloutKey = keyof typeof CALLOUTS;



function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      onClick={() => {
        navigator.clipboard.writeText(text).catch(() => {});
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }}
      className="lex-copy-btn"
      aria-label="Copy code"
    >
      {copied ? <Check size={11} /> : <Copy size={11} />}
      <span>{copied ? "Copied!" : "Copy"}</span>
    </button>
  );
}



function CodeBlock({
  code,
  lang,
  streaming,
}: {
  code: string;
  lang: string;
  streaming?: boolean;
}) {
 
  if (["chart", "bar-chart", "line-chart", "bar", "line"].includes(lang)) {
    return (
      <MiniChart raw={code} type={lang.includes("line") ? "line" : "bar"} />
    );
  }

  if (lang === "mermaid") {
    if (streaming) {
      return (
        <div className="lex-code-block group">
          <div className="lex-code-header">
            <div className="lex-code-lang-badge">
              <span
                className="lex-code-lang-dot"
                style={{ background: "#00ADD8" }}
              />
              <span className="lex-code-lang-name">mermaid (streaming...)</span>
            </div>
          </div>
          <div className="lex-code-body p-4 text-xs font-mono whitespace-pre-wrap text-muted-foreground">
            {code}
            <span className="lex-stream-cursor" />
          </div>
        </div>
      );
    }
    return <MermaidBlock chart={code} />;
  }

  const dotColor = LANG_COLORS[lang] ?? "#888";

  return (
    <div className="lex-code-block group">
      {/* Header bar */}
      <div className="lex-code-header">
        <div className="lex-code-lang-badge">
          <span
            className="lex-code-lang-dot"
            style={{ background: dotColor }}
          />
          <span className="lex-code-lang-name">{lang}</span>
        </div>
        <CopyButton text={code} />
      </div>

      {/* Code body */}
      <div className="lex-code-body">
        <SyntaxHighlighter
          language={lang === "text" ? undefined : lang}
          style={lexaraTheme}
          PreTag="div"
          wrapLongLines={false}
          customStyle={{
            margin: 0,
            padding: "1em 1.1em",
            background: "transparent",
            fontSize: "0.83em",
            lineHeight: "1.7",
          }}
          codeTagProps={{
            style: { fontFamily: "var(--font-mono, ui-monospace, monospace)" },
          }}
        >
          {code}
        </SyntaxHighlighter>
        {streaming && <span className="lex-stream-cursor" />}
      </div>
    </div>
  );
}



interface ChartRow {
  label: string;
  value: number;
}

function parseChartData(raw: string): {
  title: string;
  rows: ChartRow[];
} {
  const lines = raw.trim().split("\n").filter(Boolean);
  let title = "";
  const rows: ChartRow[] = [];

  for (const line of lines) {
    if (line.startsWith("#")) {
      title = line.replace(/^#+\s*/, "").trim();
      continue;
    }
    if (line.toLowerCase().startsWith("type:")) continue;
    
    const [rawLabel, rawVal] = line.split(",").map((s) => s.trim());
    const num = parseFloat(rawVal ?? "");
    if (rawLabel && !isNaN(num)) rows.push({ label: rawLabel, value: num });
  }
  return { title, rows };
}

function MiniChart({ raw, type }: { raw: string; type: "bar" | "line" }) {
  const { title, rows } = parseChartData(raw);
  if (rows.length === 0) {
    return (
      <div className="lex-chart-empty">
        <TrendingUp size={16} /> No data to display
      </div>
    );
  }

  const W = 440,
    H = 210;
  const PAD = { t: 28, r: 16, b: 48, l: 52 };
  const chartW = W - PAD.l - PAD.r;
  const chartH = H - PAD.t - PAD.b;
  const maxVal = Math.max(...rows.map((r) => r.value));
  const yTicks = [0, 0.25, 0.5, 0.75, 1].map((f) => ({
    y: PAD.t + chartH * (1 - f),
    label: Math.round(maxVal * f),
  }));

  if (type === "bar") {
    const bW = (chartW / rows.length) * 0.55;
    const gap = chartW / rows.length;
    return (
      <div className="lex-chart-block">
        {title && <div className="lex-chart-title">{title}</div>}
        <svg viewBox={`0 0 ${W} ${H}`} className="lex-chart-svg">
          <defs>
            <linearGradient id="lexBarGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="oklch(0.78 0.17 210)" />
              <stop
                offset="100%"
                stopColor="oklch(0.7 0.22 290)"
                stopOpacity="0.7"
              />
            </linearGradient>
            <linearGradient id="lexBarHover" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="oklch(0.88 0.14 200)" />
              <stop
                offset="100%"
                stopColor="oklch(0.78 0.17 210)"
                stopOpacity="0.8"
              />
            </linearGradient>
          </defs>
          {/* grid */}
          {yTicks.map(({ y, label }) => (
            <g key={label}>
              <line
                x1={PAD.l}
                y1={y}
                x2={W - PAD.r}
                y2={y}
                stroke="oklch(1 0 0/0.07)"
                strokeWidth="1"
                strokeDasharray="3 3"
              />
              <text
                x={PAD.l - 8}
                y={y + 3.5}
                textAnchor="end"
                fontSize="9"
                fill="oklch(0.5 0 0)"
              >
                {label}
              </text>
            </g>
          ))}
          {/* bars */}
          {rows.map((row, i) => {
            const bh = (row.value / maxVal) * chartH;
            const x = PAD.l + i * gap + (gap - bW) / 2;
            const y = PAD.t + chartH - bh;
            return (
              <g key={row.label}>
                {/* bar bg */}
                <rect
                  x={x}
                  y={PAD.t}
                  width={bW}
                  height={chartH}
                  rx="4"
                  fill="oklch(1 0 0/0.03)"
                />
                {/* bar fill */}
                <rect
                  x={x}
                  y={y}
                  width={bW}
                  height={bh}
                  rx="4"
                  fill="url(#lexBarGrad)"
                  opacity="0.85"
                >
                  <title>
                    {row.label}: {row.value}
                  </title>
                </rect>
                {/* value label */}
                <text
                  x={x + bW / 2}
                  y={y - 5}
                  textAnchor="middle"
                  fontSize="9"
                  fill="oklch(0.78 0.17 210)"
                  fontWeight="600"
                >
                  {row.value}
                </text>
                {/* x label */}
                <text
                  x={x + bW / 2}
                  y={H - PAD.b + 16}
                  textAnchor="middle"
                  fontSize="9"
                  fill="oklch(0.6 0 0)"
                >
                  {row.label}
                </text>
              </g>
            );
          })}
          {/* axis */}
          <line
            x1={PAD.l}
            y1={PAD.t}
            x2={PAD.l}
            y2={PAD.t + chartH}
            stroke="oklch(1 0 0/0.12)"
            strokeWidth="1"
          />
          <line
            x1={PAD.l}
            y1={PAD.t + chartH}
            x2={W - PAD.r}
            y2={PAD.t + chartH}
            stroke="oklch(1 0 0/0.12)"
            strokeWidth="1"
          />
        </svg>
      </div>
    );
  }

 
  const pts = rows.map((r, i) => ({
    x: PAD.l + (i / Math.max(rows.length - 1, 1)) * chartW,
    y: PAD.t + chartH * (1 - r.value / maxVal),
    ...r,
  }));
  const polyStr = pts.map((p) => `${p.x},${p.y}`).join(" ");
  const areaStr = `${pts[0].x},${PAD.t + chartH} ${polyStr} ${pts[pts.length - 1].x},${PAD.t + chartH}`;

  return (
    <div className="lex-chart-block">
      {title && <div className="lex-chart-title">{title}</div>}
      <svg viewBox={`0 0 ${W} ${H}`} className="lex-chart-svg">
        <defs>
          <linearGradient id="lexLineArea" x1="0" y1="0" x2="0" y2="1">
            <stop
              offset="0%"
              stopColor="oklch(0.78 0.17 210)"
              stopOpacity="0.35"
            />
            <stop
              offset="100%"
              stopColor="oklch(0.78 0.17 210)"
              stopOpacity="0.02"
            />
          </linearGradient>
        </defs>
        {yTicks.map(({ y, label }) => (
          <g key={label}>
            <line
              x1={PAD.l}
              y1={y}
              x2={W - PAD.r}
              y2={y}
              stroke="oklch(1 0 0/0.07)"
              strokeWidth="1"
              strokeDasharray="3 3"
            />
            <text
              x={PAD.l - 8}
              y={y + 3.5}
              textAnchor="end"
              fontSize="9"
              fill="oklch(0.5 0 0)"
            >
              {label}
            </text>
          </g>
        ))}
        <polygon points={areaStr} fill="url(#lexLineArea)" />
        <polyline
          points={polyStr}
          fill="none"
          stroke="oklch(0.78 0.17 210)"
          strokeWidth="2.5"
          strokeLinejoin="round"
          strokeLinecap="round"
        />
        {pts.map((p, i) => (
          <g key={i}>
            <circle
              cx={p.x}
              cy={p.y}
              r="5"
              fill="oklch(0.12 0 0)"
              stroke="oklch(0.78 0.17 210)"
              strokeWidth="2"
            >
              <title>
                {p.label}: {p.value}
              </title>
            </circle>
            <text
              x={p.x}
              y={H - PAD.b + 16}
              textAnchor="middle"
              fontSize="9"
              fill="oklch(0.6 0 0)"
            >
              {p.label}
            </text>
          </g>
        ))}
        <line
          x1={PAD.l}
          y1={PAD.t}
          x2={PAD.l}
          y2={PAD.t + chartH}
          stroke="oklch(1 0 0/0.12)"
          strokeWidth="1"
        />
        <line
          x1={PAD.l}
          y1={PAD.t + chartH}
          x2={W - PAD.r}
          y2={PAD.t + chartH}
          stroke="oklch(1 0 0/0.12)"
          strokeWidth="1"
        />
      </svg>
    </div>
  );
}

/**
 * Sanitize a Mermaid diagram string so that node labels containing special
 * characters (parentheses, commas, slashes, +, etc.) are properly quoted.
 *
 * Mermaid's flowchart parser rejects unquoted labels like:
 *   A[Label (with parens)]
 *   B[Forward + Backward Pass]
 *
 * We fix them by wrapping the label text in double-quotes:
 *   A["Label (with parens)"]
 *   B["Forward + Backward Pass"]
 *
 * We use a precise alternation to match all 11 Mermaid node shapes, targeting
 * only labels that follow node identifiers (e.g. node_id[label]).
 */
function sanitizeMermaid(chart: string): string {
  
  const needsQuote = /[(){}|+,;/<>]/;

  
  const nodeRegex =
    /\b([a-zA-Z0-9_-]+)\s*(?:\[\[([^\]\n]+)\]\]|\[\(([^)\n]+)\)\]|\(\[([^\]\n]+)\]\)|\[\/([^/\\\n]+)\/\]|\[\\([^\\]\n]+)\\\]|\(\(([^)\n]+)\)\)|\{\{([^}\n]+)\}\}|\[([^\]\n]+)\]|\(([^)\n]+)\)|\{([^}\n]+)\}|>([^\]\n]+)\])/g;

  return chart.replace(
    nodeRegex,
    (match, id, g2, g3, g4, g5, g6, g7, g8, g9, g10, g11, g12) => {
      
      const label =
        g2 || g3 || g4 || g5 || g6 || g7 || g8 || g9 || g10 || g11 || g12;
      if (!label) return match;

      const trimmed = label.trim();
      
      if (trimmed.startsWith('"') && trimmed.endsWith('"')) return match;

      if (needsQuote.test(trimmed)) {
        
        const escaped = trimmed.replace(/"/g, "'");

        
        let openBrackets = "";
        let closeBrackets = "";

        if (g2) {
          openBrackets = "[[";
          closeBrackets = "]]";
        } else if (g3) {
          openBrackets = "[(";
          closeBrackets = ")]";
        } else if (g4) {
          openBrackets = "([";
          closeBrackets = "])";
        } else if (g5) {
          openBrackets = "[/";
          closeBrackets = "/]";
        } else if (g6) {
          openBrackets = "[\\";
          closeBrackets = "\\]";
        } else if (g7) {
          openBrackets = "((";
          closeBrackets = "))";
        } else if (g8) {
          openBrackets = "{{";
          closeBrackets = "}}";
        } else if (g9) {
          openBrackets = "[";
          closeBrackets = "]";
        } else if (g10) {
          openBrackets = "(";
          closeBrackets = ")";
        } else if (g11) {
          openBrackets = "{";
          closeBrackets = "}";
        } else if (g12) {
          openBrackets = ">";
          closeBrackets = "]";
        }

        return `${id}${openBrackets}"${escaped}"${closeBrackets}`;
      }

      return match;
    },
  );
}



let mermaidInitialized = false;

function MermaidBlock({ chart }: { chart: string }) {
  const [svg, setSvg] = useState<string>("");
  const [error, setError] = useState<boolean>(false);

  useEffect(() => {
    let active = true;

    async function renderChart() {
      const id = `mermaid-${Math.random().toString(36).slice(2, 9)}`;
      try {
        const mermaid = (await import("mermaid")).default;
        if (!mermaidInitialized) {
          mermaid.initialize({
            startOnLoad: false,
            theme: "dark",
            securityLevel: "loose",
            fontFamily: "var(--font-mono, ui-monospace, monospace)",
            themeVariables: {
              background: "transparent",
              primaryColor: "#111827",
              primaryTextColor: "#cdd6f4",
              primaryBorderColor: "#06b6d4",
              lineColor: "#06b6d4",
              secondaryColor: "#111827",
              tertiaryColor: "#111827",
              noteBkgColor: "#1f2937",
              noteTextColor: "#cdd6f4",
              noteBorderColor: "#8b5cf6",
              actorBkg: "#111827",
              actorBorder: "#06b6d4",
              actorTextColor: "#cdd6f4",
              signalColor: "#06b6d4",
              signalTextColor: "#cdd6f4",
            },
          });
          mermaidInitialized = true;
        }

        const { svg: renderedSvg } = await mermaid.render(
          id,
          sanitizeMermaid(chart),
        );

        if (active) {
          setSvg(renderedSvg);
          setError(false);
        }
      } catch (err) {
        console.error("Mermaid render error:", err);
        try {
          const el1 = document.getElementById(id);
          if (el1) el1.remove();
          const el2 = document.getElementById(`d${id}`);
          if (el2) el2.remove();
          const uniquePart = id.split("-")[1];
          if (uniquePart) {
            const matches = document.querySelectorAll(`[id*="${uniquePart}"]`);
            matches.forEach((el) => el.remove());
          }
        } catch (e) {}
        if (active) {
          setError(true);
        }
      }
    }

    renderChart();

    return () => {
      active = false;
    };
  }, [chart]);

  if (error) {
    return (
      <div className="lex-code-block group">
        <div className="lex-code-header">
          <div className="lex-code-lang-badge">
            <span
              className="lex-code-lang-dot"
              style={{ background: "#ef4444" }}
            />
            <span className="lex-code-lang-name">mermaid (render failed)</span>
          </div>
        </div>
        <div className="lex-code-body">
          <pre className="m-0 p-4 text-xs font-mono overflow-auto text-destructive bg-transparent whitespace-pre">
            <code>{chart}</code>
          </pre>
        </div>
      </div>
    );
  }

  if (!svg) {
    return (
      <div className="flex flex-col items-center justify-center p-8 rounded-xl border border-border/40 bg-white/3 text-xs text-muted-foreground animate-pulse my-4">
        <span>Generating diagram...</span>
      </div>
    );
  }

  return (
    <div
      className="lex-mermaid-block"
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
}



function CalloutCard({
  type,
  children,
}: {
  type: CalloutKey;
  children: React.ReactNode;
}) {
  const { Icon, label, cls } = CALLOUTS[type];
  return (
    <div className={`lex-callout ${cls}`} role="note">
      <div className="lex-callout-header">
        <Icon size={13} className="lex-callout-icon" />
        <span className="lex-callout-label">{label}</span>
      </div>
      <div className="lex-callout-body">{children}</div>
    </div>
  );
}



function BlockquoteWrapper({
  children,
  node,
}: {
  children: React.ReactNode;
  
  node?: any;
}) {
  
  try {
    const firstText: string = node?.children?.[0]?.children?.[0]?.value ?? "";
    const match = firstText.match(
      /^\[!(NOTE|TIP|WARNING|CAUTION|IMPORTANT)\]/i,
    );
    if (match) {
      const key = match[1].toUpperCase() as CalloutKey;
      const remaining = firstText.slice(match[0].length).trim();
      const childArr = React.Children.toArray(children);
      const body = remaining
        ? [
            <p key="_first" className="lex-md-p">
              {remaining}
            </p>,
            ...childArr.slice(1),
          ]
        : childArr.slice(1);
      return <CalloutCard type={key}>{body}</CalloutCard>;
    }
  } catch {
   
  }
  return <blockquote className="lex-blockquote">{children}</blockquote>;
}



function TableWrapper({ children }: { children: React.ReactNode }) {
  return (
    <div className="lex-table-scroll">
      <table className="lex-table">{children}</table>
    </div>
  );
}



function TaskCheckbox({ checked }: { checked?: boolean }) {
  return (
    <span
      className={`lex-checkbox ${checked ? "lex-checkbox-on" : "lex-checkbox-off"}`}
    >
      {checked && <Check size={9} strokeWidth={3} />}
    </span>
  );
}



export function ChatMarkdown({ content, streaming }: ChatMarkdownProps) {
  const normalized = normalizeContent(content, streaming);

  const components: Components = {
    
    p({ children }) {
      return <p className="lex-md-p">{children}</p>;
    },

    
    h1({ children }) {
      return <h1 className="lex-h lex-h1">{children}</h1>;
    },
    h2({ children }) {
      return <h2 className="lex-h lex-h2">{children}</h2>;
    },
    h3({ children }) {
      return <h3 className="lex-h lex-h3">{children}</h3>;
    },
    h4({ children }) {
      return <h4 className="lex-h lex-h4">{children}</h4>;
    },
    h5({ children }) {
      return <h5 className="lex-h lex-h5">{children}</h5>;
    },
    h6({ children }) {
      return <h6 className="lex-h lex-h6">{children}</h6>;
    },

    
    pre({ children }) {
      
      
      return <>{children}</>;
    },
    code({ className, children }) {
      const lang = className?.replace("language-", "") ?? "";
      const codeStr = String(children).replace(/\n$/, "");
      
      if (lang || codeStr.includes("\n")) {
        return (
          <CodeBlock
            code={codeStr}
            lang={lang || "text"}
            streaming={streaming}
          />
        );
      }
      
      return <code className="lex-code-inline">{children}</code>;
    },

    
    table({ children }) {
      return <TableWrapper>{children}</TableWrapper>;
    },
    thead({ children }) {
      return <thead className="lex-thead">{children}</thead>;
    },
    tbody({ children }) {
      return <tbody>{children}</tbody>;
    },
    tr({ children }) {
      return <tr className="lex-tr">{children}</tr>;
    },
    
    th({ children, style }: any) {
      return (
        <th className="lex-th" style={style}>
          {children}
        </th>
      );
    },
    
    td({ children, style }: any) {
      return (
        <td className="lex-td" style={style}>
          {children}
        </td>
      );
    },

    
    
    blockquote({ children, node }: any) {
      return <BlockquoteWrapper node={node}>{children}</BlockquoteWrapper>;
    },

    
    ul({ children }) {
      return <ul className="lex-ul">{children}</ul>;
    },
    ol({ children }) {
      return <ol className="lex-ol">{children}</ol>;
    },
    
    li({ children, className }: any) {
      const isTask = String(className ?? "").includes("task-list-item");
      return (
        <li className={`lex-li ${isTask ? "lex-task-li" : ""}`}>{children}</li>
      );
    },

    
    strong({ children }) {
      return <strong className="lex-strong">{children}</strong>;
    },
    em({ children }) {
      return <em className="lex-em">{children}</em>;
    },
    del({ children }) {
      return <del className="lex-del">{children}</del>;
    },

    
    a({ href, children }) {
      return (
        <a
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className="lex-link"
        >
          {children}
          <ExternalLink size={10} className="lex-link-icon" />
        </a>
      );
    },

    
    img({ src, alt }) {
      return (
        <span className="lex-img-wrap">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={src} alt={alt ?? ""} className="lex-img" />
          {alt && <span className="lex-img-caption">{alt}</span>}
        </span>
      );
    },

    
    hr() {
      return <hr className="lex-hr" />;
    },

    
    
    input({ type, checked }: any) {
      if (type === "checkbox") return <TaskCheckbox checked={checked} />;
      return null;
    },
  };

  return (
    <div className="lex-md-body">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {normalized}
      </ReactMarkdown>
      {streaming && content !== "" && (
        <span className="lex-stream-cursor" aria-hidden />
      )}
    </div>
  );
}

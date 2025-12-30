// src/GojoConfig.js

export const setupGojoLang = (monaco) => {
  // --- KORUMA KODU BAŞLANGICI ---
  // Eğer 'gojo' dili zaten eklenmişse dur, tekrar ekleme yapma.
  if (monaco.languages.getLanguages().some(lang => lang.id === "gojo")) {
    return;
  }
  // --- KORUMA KODU BİTİŞİ ---

  // 1. Dili Kaydet
  monaco.languages.register({ id: "gojo" });

  // 2. Renklendirme Kuralları
  monaco.languages.setMonarchTokensProvider("gojo", {
    defaultToken: "",
    tokenPostfix: ".gj",

    // Gojo Lang Keywords
    keywords: [
      "fun", "cursed", "return", 
      "if", "else", "finn", 
      "while", "end", 
      "for", "to", "but", "con",
      "input", "add"
    ],

    // Tipler ve Tanımlar
    typeKeywords: [
      "int", "string", "double", "bool", "char", "array", "void"
    ],

    operators: [
      "=", ">", "<", "!", "isnt", "&&", "||", "+=", "+", "-", "*", "/", "%"
    ],

    // Standart Kütüphane
    builtins: [
      "print", "println", "random", "len", "sqrt", "floor", "ceil", "pow", "abs"
    ],

    tokenizer: {
      root: [
        // Tanımlayıcılar
        [/[a-zA-Z_]\w*/, {
          cases: {
            "@keywords": "keyword",
            "@typeKeywords": "type",
            "@builtins": "predefined",
            "@default": "identifier"
          }
        }],

        // Gojo Özel Operatörü
        [/isnt/, "operator.special"], 

        // Sayılar
        [/\d+/, "number"],
        [/\d+\.\d+/, "number.float"],

        // Stringler
        [/"/, { token: "string.quote", bracket: "@open", next: "@string" }],

        // Yorum Satırları (# ile başlar)
        [/#.*$/, "comment"],
      ],

      string: [
        [/[^\\"]+/, "string"],
        [/"/, { token: "string.quote", bracket: "@close", next: "@pop" }]
      ]
    }
  });

  // 3. Otomatik Tamamlama (Snippets)
  monaco.languages.registerCompletionItemProvider("gojo", {
    provideCompletionItems: (model, position) => {
      const suggestions = [
        {
          label: "fun",
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: [
            'fun ${1:isim}(${2:parametre})',
            '\t$0',
            'cursed'
          ].join('\n'),
          documentation: "Fonksiyon Tanımı"
        },
        {
          label: "println",
          kind: monaco.languages.CompletionItemKind.Function,
          insertText: 'println "${1:mesaj}"',
          documentation: "Ekrana yazdır"
        },
        {
          label: "domain_expansion",
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: [
            'fun domain_expansion()',
            '\tprintln "DOMAIN EXPANSION: Infinite Void"',
            '\treturn "Win"',
            'cursed'
          ].join('\n'),
          documentation: "Alan Genişletme Tekniği"
        }
      ];
      return { suggestions: suggestions };
    }
  });

  // 4. Tema: Jujutsu Kaisen Moru
  monaco.editor.defineTheme("gojo-dark", {
    base: "vs-dark",
    inherit: true,
    rules: [
      { token: "keyword", foreground: "C586C0", fontStyle: "bold" }, 
      { token: "type", foreground: "4EC9B0" },
      { token: "string", foreground: "CE9178" },
      { token: "operator.special", foreground: "FF0000", fontStyle: "bold" },
      { token: "comment", foreground: "6A9955" },
      { token: "predefined", foreground: "DCDCAA" }
    ],
    colors: {
      "editor.background": "#1E1E1E",
    }
  });
};
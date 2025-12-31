import React, { useState, useEffect, useRef } from "react";
import Editor from "@monaco-editor/react";
import { setupGojoLang } from "./GojoConfig";

// --- JUJUTSU PARŞÖMENİ (DOKÜMANTASYON VERİSİ) ---
const GOJO_DOCS = [
  {
    category: "Temel Yapı & Değişkenler",
    items: [
      { syntax: 'int sayi = 10', desc: 'Tam sayı tanımlama.' },
      { syntax: 'string isim = "Gojo"', desc: 'Metin tanımlama.' },
      { syntax: 'double oran = 3.14', desc: 'Ondalıklı sayı.' },
      { syntax: 'bool durum = true', desc: 'Mantıksal değer (true/false).' },
      { syntax: 'array[] liste', desc: 'Boş bir dinamik dizi oluşturur.' }
    ]
  },
  {
    category: "Tip Dönüşümleri (ÖNEMLİ!)",
    items: [
      { syntax: 'str(10)', desc: 'Sayıyı yazıya çevirir (Birleştirme için şart).' },
      { syntax: 'int("10")', desc: 'Yazıyı tam sayıya çevirir.' },
      { syntax: 'float("3.14")', desc: 'Yazıyı ondalıklı sayıya çevirir.' }
    ]
  },
  {
    category: "Giriş / Çıkış (I/O)",
    items: [
      { syntax: 'print "Mesaj"', desc: 'Ekrana yazar (Alt satıra geçmez).' },
      { syntax: 'println "Mesaj"', desc: 'Ekrana yazar ve alt satıra geçer.' },
      { syntax: 'input "Adın ne?: "', desc: 'Kullanıcıdan veri alır.' }
    ]
  },
  {
    category: "Kontrol Yapıları",
    items: [
      { syntax: 'if x > 10 ... finn', desc: 'Eğer koşulu bloğu.' },
      { syntax: 'if ... else ... finn', desc: 'Eğer - Değilse bloğu.' },
      { syntax: 'while x > 0 ... end', desc: 'While döngüsü.' },
      { syntax: 'for i = 1 to 10 ... con', desc: 'For döngüsü.' },
      { syntax: 'for i = 1 to 10 but 2 ... con', desc: '2\'şer atlayan döngü.' }
    ]
  },
  {
    category: "Fonksiyonlar (Teknikler)",
    items: [
      { syntax: 'fun topla(a,b) ... cursed', desc: 'Fonksiyon tanımlama.' },
      { syntax: 'return x', desc: 'Fonksiyondan değer döndürür.' },
      { syntax: 'topla(10, 20)', desc: 'Fonksiyon çağırma.' }
    ]
  },
  {
    category: "Dizi (Array) İşlemleri",
    items: [
      { syntax: 'add((liste) "Eleman")', desc: 'Diziye eleman ekler.' },
      { syntax: 'liste += "Eleman"', desc: 'Alternatif ekleme yöntemi.' },
      { syntax: 'len(liste)', desc: 'Dizinin uzunluğunu verir.' },
      { syntax: 'liste[0] = "Yeni"', desc: 'Eleman değiştirme.' }
    ]
  },
  {
    category: "Matematik & Random",
    items: [
      { syntax: 'random(1, 100)', desc: 'Rastgele sayı üretir.' },
      { syntax: 'sqrt(16)', desc: 'Karekök alır (Sonuç: 4.0).' },
      { syntax: 'pow(2, 3)', desc: 'Üs alma (2^3 = 8.0).' },
      { syntax: 'floor(3.9)', desc: 'Aşağı yuvarlama (3).' },
      { syntax: 'ceil(3.1)', desc: 'Yukarı yuvarlama (4).' },
      { syntax: 'abs(-50)', desc: 'Mutlak değer.' }
    ]
  },
  {
    category: "Operatörler",
    items: [
      { syntax: 'isnt', desc: 'Eşit değildir (!= yerine).' },
      { syntax: '&&', desc: 'VE operatörü.' },
      { syntax: '||', desc: 'VEYA operatörü.' },
      { syntax: '!', desc: 'DEĞİL operatörü.' }
    ]
  }
];

// Örnek Kodlar
const EXAMPLES = {
  "test": `println "=== JUJUTSU KAISEN: TEST ==="\n\nint power = 100\n\nif power > 50\n    println "Cursed Energy High!"\nelse\n    println "Weak..."\nfinn`,
  "zar_oyunu": `println "=== GOJO ZAR OYUNU ==="\n\nint bakiye = 100\nint bahis\nint zar1\nint zar2\n\nwhile bakiye > 0\n    println "Mevcut Bakiyen: {bakiye} TL"\n    bahis = input "Bahis gir (Cikis icin 0): "\n    \n    if bahis == 0\n        println "Oyundan cikiliyor..."\n        bakiye = -1\n    else\n        if bahis > bakiye\n            println "Yetersiz bakiye!"\n        else\n            zar1 = random(1, 6)\n            zar2 = random(1, 6)\n            \n            println "Zarlar atiliyor... {zar1} - {zar2}"\n            \n            if zar1 + zar2 > 7\n                println "Kazandin! ({zar1 + zar2} > 7)"\n                bakiye = bakiye + bahis\n            else\n                println "Kaybettin..."\n                bakiye = bakiye - bahis\n            finn\n        finn\n    finn\n    println "------------------"\nend\nprintln "Oyun Bitti."`,
  "hesap_makinesi": `println "--- GOJO HESAP MAKINESI ---"\n\nbool calisiyor = true\n\nwhile calisiyor\n    println ""\n    println "==== MENU ===="\n    println "1. Toplama (+)"\n    println "2. Cikarma (-)"\n    println "3. Carpma (*)"\n    println "4. Bolme (/)"\n    println "5. Mod Alma (%)"\n    println "0. Cikis"\n    println "=============="\n\n    int secim = input "Islem Numarasi Secin: "\n\n    if secim == 0\n        println "Gule gule..."\n        calisiyor = false\n    else\n        double s1 = input "Birinci Sayi: "\n        double s2 = input "Ikinci Sayi: "\n\n        println "----------------"\n\n        if secim == 1\n            println "SONUC: {s1} + {s2} = {s1 + s2}"\n        finn\n        if secim == 2\n             println "SONUC: {s1} - {s2} = {s1 - s2}"\n        finn\n        if secim == 3\n            println "SONUC: {s1} * {s2} = {s1 * s2}"\n        finn\n        if secim == 4\n            if s2 isnt 0\n                println "SONUC: {s1} / {s2} = {s1 / s2}"\n            else\n                println "HATA: Sifira bolunemez!"\n            finn\n        finn\n        if secim == 5\n             println "SONUC: {s1} % {s2} = {s1 % s2}"\n        finn\n        println "----------------"\n    finn\nend`,
  "fonksiyonlar": `println "=== JUJUTSU KAISEN: CURSED TECHNIQUES ==="\n\nfun topla(sayi1, sayi2)\n    println "   > Teknik Calisiyor: {sayi1} + {sayi2}"\n    return sayi1 + sayi2\ncursed\n\nfun domain_expansion()\n    return "   > DOMAIN EXPANSION: Infinite Void"\ncursed\n\nprintln "[1] Toplama Teknigi Deneniyor..."\nint sonuc = topla(30, 50)\nprintln "   > Sonuc: {sonuc}"\n\nprintln "[2] Alan Genisletme..."\nprintln domain_expansion()`
};

const STORAGE_KEY = "gojo_lang_autosave";

function App() {
  const [output, setOutput] = useState("Sistem başlatılıyor...\n");
  const [isRunning, setIsRunning] = useState(false);
  const [pyodide, setPyodide] = useState(null);
  
  // Efekt ve Panel Durumları
  const [runStatus, setRunStatus] = useState("idle"); // idle, success, error
  const [showDocs, setShowDocs] = useState(false); // Dokümantasyon açık mı?

  const editorRef = useRef(null);
  const fileInputRef = useRef(null);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
  
  // Başlangıç kodunu hafızadan veya örnekten al
  const initialCode = localStorage.getItem(STORAGE_KEY) || EXAMPLES["test"];

  // Pencere boyutu izleyici
  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Terminal Köprüsü (Python -> React)
  useEffect(() => {
    window.writeToTerminal = (text) => {
      setOutput((prev) => prev + text);
      const term = document.getElementById("live-terminal");
      if (term) {
        term.textContent += text;
        term.scrollTop = term.scrollHeight;
      }
    };
    return () => { delete window.writeToTerminal; };
  }, []);

  // Monaco Editör Ayarları
  const handleEditorWillMount = (monaco) => setupGojoLang(monaco);
  const handleEditorDidMount = (editor, monaco) => { editorRef.current = editor; };

  // Pyodide Başlatıcı
  useEffect(() => {
    const initPyodide = async () => {
      try {
        const py = await window.loadPyodide();
        const files = ["core.py", "state.py", "stdlib.py", "utils.py", "main.py"];
        for (const file of files) {
          const response = await fetch(`/gojo_source/${file}`);
          if (!response.ok) throw new Error(`${file} yüklenemedi`);
          const content = await response.text();
          py.FS.writeFile(file, content);
        }
        setPyodide(py);
        setOutput("Gojo Lang v7.0 Hazır!\nKodunuzu yazıp 'ÇALIŞTIR' butonuna basın.\nSağ üstteki kitaba tıklayarak komutları görebilirsin.\n");
      } catch (err) {
        setOutput(`Başlatma Hatası: ${err.message}`);
      }
    };
    initPyodide();
  }, []);

  // İndirme İşlevi
  const handleDownload = () => {
    const code = editorRef.current.getValue();
    if (!code) return;
    const blob = new Blob([code], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "gojo_script.gj";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Yükleme İşlevleri
  const handleUploadClick = () => fileInputRef.current.click();

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target.result;
      if (editorRef.current) {
        editorRef.current.setValue(content);
        localStorage.setItem(STORAGE_KEY, content);
      }
    };
    reader.readAsText(file);
    event.target.value = "";
  };

  // ÇALIŞTIRMA MANTIĞI
  const handleRun = async () => {
    if (!pyodide) return;
    setIsRunning(true);
    setRunStatus("idle");
    
    setOutput(""); 
    const term = document.getElementById("live-terminal");
    if (term) term.textContent = "--- Program Başlatıldı ---\n";
    setOutput("--- Program Başlatıldı ---\n");
    const userCode = editorRef.current.getValue();

    try {
      pyodide.FS.writeFile("script.gj", userCode);
      
      await pyodide.runPythonAsync(`
        import sys
        import builtins
        import state
        from core import run_gojo
        from js import prompt, window

        error_occurred = False
        last_printed_line = ""

        class JSStdout:
            def write(self, text):
                global last_printed_line, error_occurred
                # Hata Kontrolü
                text_lower = text.lower()
                if "hata" in text_lower:
                  error_occurred = True
                
                clean_text = text.strip()
                if clean_text: last_printed_line = clean_text
                
                if hasattr(window, 'writeToTerminal'):
                    window.writeToTerminal(text)
            def flush(self): pass

        sys.stdout = JSStdout()

        def custom_input(text=""):
            global last_printed_line
            context_info = last_printed_line
            
            sys.stdout.write(text)
            
            if context_info == text.strip(): prompt_msg = text
            else: prompt_msg = f"TERMİNAL BİLGİSİ (Son Durum):\\n{context_info}\\n\\n------------------\\n{text}"
            
            val = prompt(prompt_msg)
            if val is None: val = ""
            
            sys.stdout.write(str(val) + "\\n")
            return str(val)
        
        builtins.input = custom_input
        
        # Bellek Temizliği
        state.memory.clear()
        state.var_types.clear()
        state.functions.clear()
        state.call_stack.clear()

        try:
            run_gojo("script.gj")
            # Hata varsa React'e bildir
            if error_occurred: raise Exception("Gojo Lang Hatası Tespit Edildi")
        except Exception as e: raise e 
      `);
      
      // Başarılıysa Mor Efekt
      setRunStatus("success");
      setTimeout(() => setRunStatus("idle"), 2000);

    } catch (err) {
      // Hatalıysa Kırmızı Efekt
      setRunStatus("error");
      if (!output.includes("HATA") && !output.includes("hatasi")) {
           window.writeToTerminal(`\nSistem Hatası: ${err.message}`);
      }
      setTimeout(() => setRunStatus("idle"), 2000);
    } finally {
      setIsRunning(false);
      window.writeToTerminal("\n--- Program Sonlandı ---\n");
    }
  };

  return (
    <div 
      className={
        runStatus === "success" ? "domain-expansion-success" : 
        runStatus === "error" ? "cursed-error" : ""
      }
      style={{ 
        display: "flex", 
        flexDirection: isMobile ? "column" : "row", 
        height: "100vh", 
        background: "#1e1e1e", 
        color: "#d4d4d4", 
        fontFamily: "Consolas, monospace",
        boxSizing: "border-box",
        overflow: "hidden"
      }}
    >
      <input type="file" ref={fileInputRef} onChange={handleFileChange} style={{ display: "none" }} accept=".gj,.txt" />

      {/* --- DOKÜMANTASYON PANELİ (SLIDE-IN) --- */}
      <div className={`docs-panel ${showDocs ? "open" : ""}`}>
        <button className="docs-close-btn" onClick={() => setShowDocs(false)}>×</button>
        <h2 style={{color: '#c586c0', borderBottom: '2px solid #fff', paddingBottom: '10px'}}>
          Jujutsu Parşömeni
        </h2>
        {GOJO_DOCS.map((section, idx) => (
          <div key={idx} className="doc-section">
            <span className="doc-title">{section.category}</span>
            {section.items.map((item, i) => (
              <div key={i} className="doc-item">
                <span className="doc-syntax">{item.syntax}</span>
                <span className="doc-desc">{item.desc}</span>
              </div>
            ))}
          </div>
        ))}
      </div>
      {/* -------------------------------------- */}

      {/* SOL PANEL: EDİTÖR */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", borderRight: isMobile ? "none" : "2px solid #333", borderBottom: isMobile ? "2px solid #333" : "none", height: isMobile ? "60%" : "100%" }}>
        <div style={{ padding: "10px", background: "#252526", display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "center", gap: "10px" }}>
          <span style={{ fontWeight: "bold", color: "#c586c0", whiteSpace: "nowrap" }}> GOJO IDE</span>
          
          {/* --- DÜZELTME: flexWrap ekledik ki mobilde butonlar alt alta geçebilsin --- */}
<div style={{
  display: "flex", 
  gap: "10px", 
  flex: 1, 
  justifyContent: "flex-end", 
  flexWrap: "wrap" 
}}>
            <select 
              onChange={(e) => {
                const code = EXAMPLES[e.target.value];
                if (editorRef.current) {
                  editorRef.current.setValue(code);
                  localStorage.setItem(STORAGE_KEY, code);
                }
              }}
              style={{ background: "#333", color: "white", border: "1px solid #555", padding: "5px", borderRadius: "4px", maxWidth: "150px" }}
            >
              <option value="test">Örnekler...</option>
              <option value="test">Basit Test</option>
              <option value="zar_oyunu">Zar Oyunu </option>
              <option value="hesap_makinesi">Hesap Makinesi</option>
              <option value="fonksiyonlar">Fonksiyonlar</option>
            </select>

            <button onClick={handleUploadClick} title="Dosya Aç" style={{background: "#444", color: "white", border: "1px solid #666", padding: "8px 12px", cursor: "pointer", borderRadius: "4px"}}>Aç</button>
            <button onClick={handleDownload} title="Kodu İndir" style={{background: "#444", color: "white", border: "1px solid #666", padding: "8px 12px", cursor: "pointer", borderRadius: "4px"}}>İndir</button>
            
            {/* KİTAP BUTONU */}
            <button 
              onClick={() => setShowDocs(!showDocs)} 
              title="Komut Kitabı" 
              style={{
                background: showDocs ? "#c586c0" : "#444", 
                color: "white", 
                border: "1px solid #666", 
                padding: "8px 12px", 
                cursor: "pointer", 
                borderRadius: "4px"
              }}
            >
              Tutorial
            </button>

            <button 
              onClick={handleRun}
              disabled={isRunning || !pyodide}
              style={{
                background: isRunning ? "#555" : "#0e639c",
                color: "white",
                border: "none",
                padding: "8px 15px",
                cursor: "pointer",
                borderRadius: "4px",
                fontWeight: "bold",
                whiteSpace: "nowrap"
              }}
            >
              {isMobile ? ">" : (!pyodide ? "..." : isRunning ? "..." : "ÇALIŞTIR")}
            </button>
          </div>
        </div>
        
        <Editor
          height="100%"
          theme="gojo-dark"
          defaultLanguage="gojo"
          defaultValue={initialCode}
          onChange={(value) => { localStorage.setItem(STORAGE_KEY, value || ""); }}
          beforeMount={handleEditorWillMount}
          onMount={handleEditorDidMount}
          options={{ fontSize: isMobile ? 14 : 16, minimap: { enabled: false }, padding: { top: 20 }, wordWrap: "on" }}
        />
      </div>

      {/* SAĞ PANEL: TERMİNAL */}
      <div style={{ width: isMobile ? "100%" : "40%", height: isMobile ? "40%" : "100%", display: "flex", flexDirection: "column", background: "#1e1e1e" }}>
        <div style={{ padding: "10px", background: "#252526", borderBottom: "1px solid #333", display: "flex", justifyContent: "space-between" }}>
          <span style={{fontWeight: "bold"}}>TERMİNAL</span>
          <button onClick={() => { setOutput(""); const term = document.getElementById("live-terminal"); if(term) term.textContent = ""; }} style={{background: "transparent", border: "none", color: "#888", cursor: "pointer", fontSize: "12px"}}>Temizle</button>
        </div>
        <pre id="live-terminal" style={{ flex: 1, padding: "15px", overflow: "auto", margin: 0, whiteSpace: "pre-wrap", color: "#4ec9b0", fontSize: isMobile ? "13px" : "15px" }}>{output}</pre>
      </div>
    </div>
  );
}

export default App;
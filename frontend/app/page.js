'use client'
import { useState, useEffect, useRef } from 'react'

const LANGUAGES = [
  { code: "EN-US", name: "English (US)" },
  { code: "AR", name: "Arabic" },
  { code: "ZH", name: "Chinese" },
  { code: "ES", name: "Spanish" }
]

// 首先添加一个语言名称映射
const LANGUAGE_NAMES = {
  "EN-US": "English (US)",
  "AR": "Arabic",
  "ZH": "Chinese",
  "ES": "Spanish"
}

export default function Home() {
  const [inputText, setInputText] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [selectedLanguage, setSelectedLanguage] = useState(null)
  const [isMultiLingual, setIsMultiLingual] = useState(true)
  const textareaRef = useRef(null)

  // 自动调整文本框高度
  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = `${Math.max(200, textarea.scrollHeight)}px`
    }
  }

  // 监听输入内容变化
  useEffect(() => {
    adjustTextareaHeight()
  }, [inputText])

  const handleTranslate = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:8000/api/translate/auto', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: inputText,
          target_langs: ["EN-US", "AR", "ZH", "ES"],
          single_language: isMultiLingual ? null : selectedLanguage,
          question_response: true
        }),
      })

      const data = await response.json()
      setResult(data)
    } catch (error) {
      console.error('Translation error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Multilingual AI System</h1>
        
        <div className="mb-6">
          <div className="relative bg-white rounded-2xl shadow-sm">
            <textarea
              ref={textareaRef}
              className="w-full p-6 pb-20 rounded-2xl focus:outline-none min-h-[200px] text-gray-700 overflow-hidden resize-none"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Enter text to ask a question..."
              rows={1}
            />
            <div className="absolute bottom-6 left-6 flex items-center gap-4">
              <button
                onClick={() => setIsMultiLingual(!isMultiLingual)}
                className={`flex items-center px-4 py-2 rounded-full text-sm transition-all duration-200 ${
                  isMultiLingual 
                    ? 'bg-blue-50 text-blue-600 hover:bg-blue-100' 
                    : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
                }`}
              >
                <svg 
                  className={`w-4 h-4 mr-2 ${isMultiLingual ? 'text-blue-600' : 'text-gray-600'}`} 
                  viewBox="0 0 24 24" 
                  fill="none" 
                  stroke="currentColor"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129"
                  />
                </svg>
                Multi-language Mode
              </button>
              
              {!isMultiLingual && (
                <select
                  value={selectedLanguage || ''}
                  onChange={(e) => setSelectedLanguage(e.target.value)}
                  className="p-2 border rounded-full bg-white text-sm text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-100"
                >
                  <option value="">Select Language</option>
                  {LANGUAGES.map(lang => (
                    <option key={lang.code} value={lang.code}>
                      {lang.name}
                    </option>
                  ))}
                </select>
              )}
            </div>
            
            <button
              className="absolute bottom-6 right-6 h-9 px-4 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-colors font-medium flex items-center gap-1.5 text-sm disabled:bg-blue-300 disabled:cursor-not-allowed"
              onClick={handleTranslate}
              disabled={loading || (!isMultiLingual && !selectedLanguage)}
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-3.5 w-3.5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Processing
                </>
              ) : (
                <>
                  Send
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                  </svg>
                </>
              )}
            </button>
          </div>
        </div>

        {result && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4">Translations</h2>
              <div className="grid grid-cols-2 gap-4">
                {Object.entries(result.translations).map(([lang, text]) => (
                  <div key={lang} className="border p-4 rounded">
                    <div className="font-medium">{LANGUAGE_NAMES[lang] || lang}</div>
                    <div>{text}</div>
                  </div>
                ))}
              </div>
            </div>

            {result.question_responses && (
              <div className="bg-white p-6 rounded-lg shadow">
                <h2 className="text-xl font-semibold mb-4">AI Responses</h2>
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(result.question_responses).map(([lang, response]) => (
                    <div key={lang} className="border p-4 rounded">
                      <div className="font-medium">{LANGUAGE_NAMES[lang] || lang}</div>
                      <div className="mt-2">{response}</div>
                      {result.english_responses && lang !== 'EN-US' && (
                        <div className="mt-2 text-gray-600 text-sm">
                          English: {result.english_responses[lang]}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  )
}

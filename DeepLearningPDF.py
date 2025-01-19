import fitz  
from transformers import pipeline
from fpdf import FPDF
import os
import time

# PDF'den metin çıkarma fonksiyonu (PyMuPDF kullanarak)
def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text("text")  # Sayfa başına metin çıkarıyoruz
        return text
    except Exception as e:
        print(f"PDF okuma hatası: {e}")
        return None

# Özetleme fonksiyonu (Attention mask kullanarak)
def summarize_text(text, model_name='facebook/bart-large-cnn', chunk_size=1000, max_length=512):
    try:
        summarizer = pipeline("summarization", model=model_name)
        summary = ""
        # Metni küçük parçalara bölerek özetleme yapalım
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i+chunk_size]
            
            # Attention mask ekleyerek özetleme
            inputs = summarizer.tokenizer(chunk, return_tensors="pt", padding=True, truncation=True, max_length=max_length)
            attention_mask = inputs['attention_mask']  # Bu, padding token'larının maskelenmesini sağlar
            chunk_summary = summarizer.model.generate(inputs['input_ids'], attention_mask=attention_mask)
            
            # Özet metni oluşturma
            summary += summarizer.tokenizer.decode(chunk_summary[0], skip_special_tokens=True) + " "
        return summary.strip()
    except Exception as e:
        print(f"Özet çıkarma hatası: {e}")
        return None

# PDF oluşturma fonksiyonu (Türkçe karakterler için font eklemeleri yapıldı)
def create_pdf(text, output_path):
    try:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Türkçe karakter desteği için fontu ekleyin (Arial Unicode MS veya benzeri)
        font_path = r"C:\Users\Yusuf\Desktop\arial.ttf"  # Buraya doğru font yolunu verin
        pdf.add_font("ArialUnicode", "", font_path, uni=True)  # Unicode desteği sağlanacak
        pdf.set_font("ArialUnicode", size=12)

        # PDF'e metni ekliyoruz
        pdf.multi_cell(0, 10, text)  # Çok satırlı metin    
        pdf.output(output_path)  # PDF dosyasını kaydediyoruz
        print(f"Özet PDF dosyası kaydedildi: {output_path}")
    except Exception as e:
        print(f"PDF oluşturma hatası: {e}")

# PDF dosyalarının birleştirilmesi
def merge_pdfs(pdf_list, output_path):
    from PyPDF2 import PdfMerger

    try:
        merger = PdfMerger()

        for pdf in pdf_list:
            merger.append(pdf)

        merger.write(output_path)
        merger.close()
        print(f"PDF dosyaları başarıyla birleştirildi: {output_path}")
    except Exception as e:
        print(f"PDF birleştirme hatası: {e}")

# Ana fonksiyon
def firstStep(pdfPaths, courseName, output_folder):
    start_time = time.time()
    print("Üretime Başlanıyor")

    # Kurs başlığını PDF'ye kaydedelim
    course_title_pdf_path = os.path.join(output_folder, f"{courseName}_Course.pdf")
    

    # Metin çıkarma ve özetleme
    full_text = ""
    for pdfPath in pdfPaths:
        print(f"{pdfPath} dosyasından metin çıkarılıyor...")
        text = extract_text_from_pdf(pdfPath)
        if text:
            full_text += text + "\n\n"

    # Eğer PDF metin içeriyorsa, özet çıkarma
    if full_text.strip():
        summary = summarize_text(full_text)
        if not summary:
            print("Özet çıkarılamadı!")
            return

        # Özet PDF oluşturma
        summary_pdf_path = os.path.join(output_folder, f"{courseName}_Summary.pdf")
        create_pdf(summary, summary_pdf_path)

        # PDF dosyalarını birleştirme
        output_combined_pdf_path = os.path.join(output_folder, f"{courseName}_Full_Summary.pdf")
        merge_pdfs([course_title_pdf_path, summary_pdf_path], output_combined_pdf_path)

        end_time = time.time()
        elapsed_time = end_time - start_time
        minutes, seconds = divmod(int(elapsed_time), 60)
        print(f"İşlem tamamlandı. Birleştirilmiş PDF: {output_combined_pdf_path}")
        print(f"Geçen süre: {minutes} dakika {seconds} saniye")

    else:
        print("PDF dosyasından metin çıkarılamadı!")

# PDF yolları
pdfPaths = [r"C:\Users\BarisYasin\Desktop\Çavdar tarlasında çocuklar.pdf"]  # Özet alınacak olan PDF
courseName = "Özet"  # Kurs adı (özet adı)
output_folder = r"C:\Users\BarisYasin\Desktop\Python"  # Çıktı dosyasının kaydedileceği klasör

# İşlem başlatma
firstStep(pdfPaths, courseName, output_folder)

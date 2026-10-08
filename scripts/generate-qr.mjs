import QRCode from 'qrcode';
import fs from 'node:fs';
const url=process.env.SITE_URL||'https://asis-digital-san-miguel-2025.jimdev.chatgpt.site';
fs.mkdirSync('public/share',{recursive:true});
await QRCode.toFile('public/share/qr-asis.png',url,{width:1000,margin:4,errorCorrectionLevel:'M',color:{dark:'#3c5395',light:'#ffffff'}});
fs.writeFileSync('public/share/qr-asis.svg',await QRCode.toString(url,{type:'svg',margin:4,errorCorrectionLevel:'M',color:{dark:'#3c5395',light:'#ffffff'}}));
console.log('QR generated for configured public destination.');

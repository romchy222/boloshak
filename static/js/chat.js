document.querySelector('.bbx-send').addEventListener('click', () => {
  const input = document.querySelector('.bbx-input');
  if (input.value.trim() !== '') {
    alert('Message sent: ' + input.value);
    input.value = '';
  }
});
document.querySelector('.bbx-input').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    document.querySelector('.bbx-send').click();
  }
});
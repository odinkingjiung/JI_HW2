const cards = document.querySelector('#cards');
const chart = document.querySelector('#chart');
const statusText = document.querySelector('#status');
const errorText = document.querySelector('#error');
const refresh = document.querySelector('#refresh');

function render(data) {
  const max = Math.max(...data.games.map(game => game.players), 1);
  cards.innerHTML = data.games.map(game => `<article class="card"><h2>${game.name}</h2><div class="number">${game.players.toLocaleString('ko-KR')}</div><span class="unit">현재 접속자</span></article>`).join('');
  chart.innerHTML = data.games.map(game => `<div class="bar-wrap"><strong>${game.players.toLocaleString('ko-KR')}</strong><div class="bar" style="height:${Math.max(game.players / max * 100, 3)}%"></div><div class="label">${game.name}</div></div>`).join('');
  statusText.textContent = `마지막 업데이트: ${new Date(data.updated_at).toLocaleTimeString('ko-KR')}`;
}
async function loadPlayers() {
  refresh.disabled = true; errorText.textContent = ''; statusText.textContent = '불러오는 중...';
  try { const response = await fetch('/api/players'); const data = await response.json(); if (!response.ok) throw new Error(data.error); render(data); }
  catch (error) { errorText.textContent = error.message || '데이터를 불러오지 못했습니다.'; statusText.textContent = '조회 실패'; }
  finally { refresh.disabled = false; }
}
refresh.addEventListener('click', loadPlayers); loadPlayers();
